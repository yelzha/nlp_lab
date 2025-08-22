import re
import uuid
import math
from dataclasses import dataclass
from typing import List, Dict, Tuple

import torch
import numpy as np
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    AutoModelForCausalLM,
    pipeline,
)
from sentence_transformers import SentenceTransformer

# -----------------------------
# Config and utilities
# -----------------------------

@dataclass
class DecodeCfg:
    do_sample: bool
    num_beams: int
    top_p: float
    temperature: float
    repetition_penalty: float
    max_new_tokens: int = 256


PIVOT_MENUS = {
    # Tuned for English source; pick what your MT supports well.
    1: [["nl"], ["da"]],                                # light
    2: [["fr", "de"], ["es", "de"]],                   # medium
    3: [["fr", "de"], ["es", "it"], ["pt", "de"]],
    4: [["tr"], ["fi"]],                               # strong
    5: [["tr", "es"], ["ja", "es"]],                   # very strong
}

SIM_THRESH = {1: 0.92, 2: 0.90, 3: 0.88, 4: 0.86, 5: 0.84}

BIGRAM_OVERLAP_CEIL = {3: 0.75, 4: 0.70, 5: 0.65}  # stricter for stronger paraphrases

KEEP_PREFIX = "{{KEEP_"  # sturdy placeholders the models rarely mangle
KEEP_SUFFIX = "}}"

# Regexes to protect math, code, URLs/emails, and numbers+units
RE_BLOCK_CODE = re.compile(r"```.+?```", re.DOTALL)
RE_INLINE_CODE = re.compile(r"`[^`]+`")
RE_LATEX_DOLLARS_BLOCK = re.compile(r"\$\$(?:\\\$|[^$])+\$\$", re.DOTALL)
RE_LATEX_DOLLARS_INLINE = re.compile(r"(?<!\$)\$(?:\\\$|[^$])+\$")
RE_LATEX_PARENS = re.compile(r"\\\((?:\\\)|[^\)])+\\\)")
RE_LATEX_BRACKS = re.compile(r"\\\[(?:\\\]|[^\]])+\\\]")
RE_URL = re.compile(r"(https?://[^\s]+)")
RE_EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
# Numbers with optional unit/symbol (%, °C, km, ms, μs, Ω, etc.)
RE_NUM_UNITS = re.compile(r"\b\d+(?:[.,]\d+)?\s?(?:%|°[CF]|[A-Za-zµμΩΔπ·⋅×*/^−\-]+)?\b")

# Very light sentence splitter (keeps punctuation)
RE_SENT_SPLIT = re.compile(r"(?<=[.!?;:])\s+(?=[A-Z0-9$`\\])")


def bigram_overlap(a: str, b: str) -> float:
    def grams(s):
        toks = s.lower().split()
        return set(zip(toks, toks[1:])) if len(toks) > 1 else set()
    A, B = grams(a), grams(b)
    return len(A & B) / max(1, len(A))


def choose_pivots(level: int) -> List[str]:
    menus = PIVOT_MENUS.get(level, PIVOT_MENUS[2])
    # Pick deterministically: first menu; you can randomize if you want diversity.
    return menus[0]


def decode_cfg_for_level(level: int) -> DecodeCfg:
    if level <= 1:
        return DecodeCfg(do_sample=False, num_beams=4, top_p=0.0, temperature=1.0, repetition_penalty=1.05)
    if level == 2:
        return DecodeCfg(do_sample=True, num_beams=1, top_p=0.85, temperature=0.9, repetition_penalty=1.05)
    if level == 3:
        return DecodeCfg(do_sample=True, num_beams=1, top_p=0.9, temperature=0.95, repetition_penalty=1.07)
    if level == 4:
        return DecodeCfg(do_sample=True, num_beams=1, top_p=0.93, temperature=1.0, repetition_penalty=1.1)
    return DecodeCfg(do_sample=True, num_beams=1, top_p=0.95, temperature=1.05, repetition_penalty=1.12)


# -----------------------------
# Protect & restore spans
# -----------------------------

PROTECTORS = [
    RE_BLOCK_CODE, RE_INLINE_CODE,
    RE_LATEX_DOLLARS_BLOCK, RE_LATEX_DOLLARS_INLINE,
    RE_LATEX_PARENS, RE_LATEX_BRACKS,
    RE_URL, RE_EMAIL, RE_NUM_UNITS
]

def protect_spans(text: str) -> Tuple[str, Dict[str, str]]:
    mapping = {}
    def _sub_one(match):
        token = f"{KEEP_PREFIX}{uuid.uuid4().hex[:8]}{KEEP_SUFFIX}"
        mapping[token] = match.group(0)
        return token
    protected = text
    for rex in PROTECTORS:
        protected = rex.sub(_sub_one, protected)
    return protected, mapping


def restore_spans(text: str, mapping: Dict[str, str]) -> str:
    # Robust restore even if spaces snuck in: remove accidental spaces inside tokens.
    def normalize_tokens(t: str) -> str:
        return re.sub(r"\{\s*\{?\s*KEEP_([A-Fa-f0-9]{8})\s*\}?\s*\}", r"{{KEEP_\1}}", t)
    t = normalize_tokens(text)
    for k, v in mapping.items():
        t = t.replace(k, v)
    return t


# -----------------------------
# Models
# -----------------------------

class MT:
    """
    facebook/m2m100_418M multilingual MT
    """
    def __init__(self, device=None):
        self.model_name = "facebook/m2m100_418M"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

    def translate(self, text: str, src_lang: str, tgt_lang: str, cfg: DecodeCfg) -> str:
        self.tokenizer.src_lang = src_lang
        inputs = self.tokenizer(text, return_tensors="pt", padding=False).to(self.model.device)
        forced_bos_token_id = self.tokenizer.get_lang_id(tgt_lang)
        with torch.no_grad():
            out = self.model.generate(
                **inputs,
                forced_bos_token_id=forced_bos_token_id,
                do_sample=cfg.do_sample,
                num_beams=cfg.num_beams,
                top_p=cfg.top_p,
                temperature=cfg.temperature,
                repetition_penalty=cfg.repetition_penalty,
                max_new_tokens=cfg.max_new_tokens,
            )
        return self.tokenizer.decode(out[0], skip_special_tokens=True)


class Refiner:
    """
    Small instruction LLM for English fluency/style.
    Uses chat template + XML output box to avoid prompt bleed.
    """
    def __init__(self, device=None, model_name="microsoft/Phi-3-mini-4k-instruct"):
        self.model_name = model_name
        self.tok = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        )
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

        # Some chat models define a special end token in their template. Fall back to eos.
        self.eos_id = getattr(self.tok, "eos_token_id", None)
        # If the tokenizer exposes an "apply_chat_template" end token, use it automatically.

    def _apply_template(self, system: str, user: str) -> str:
        # Use the official chat template so the model knows what is system/user/assistant
        if hasattr(self.tok, "apply_chat_template"):
            messages = [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ]
            return self.tok.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
        # Fallback (rare): minimal manual prompt
        return f"<|system|>\n{system}\n<|user|>\n{user}\n<|assistant|>\n"

    @staticmethod
    def _extract_xml(text: str) -> str:
        # Return only content inside <out>...</out>; else return the last assistant block.
        m = re.search(r"<out>\s*(.*?)\s*</out>", text, flags=re.DOTALL | re.IGNORECASE)
        if m:
            return m.group(1).strip()
        # Generic cleanup if model ignored XML box
        text = re.sub(r"(?is)^.*?<\|assistant\|>\s*", "", text)  # drop prelude
        # Remove common boilerplate echoes
        text = re.sub(r"(?is)you are an editor\..*?avoid near-copying.*?\n", "", text)
        text = re.sub(r"(?im)^\s*(STYLE:.*|TEXT:.*|SOURCE:.*|OUTPUT:.*)\s*", "", text)
        return text.strip()

    def refine(self, text: str, style: str = "neutral") -> str:
        system = (
            "You are an expert copy editor. Improve fluency and readability while preserving meaning. "
            "Do NOT modify tokens like {{KEEP_xxxx}}. Keep math/LaTeX, code, URLs, and numbers exactly as-is. "
            "Return ONLY the final text inside <out>...</out> with no extra words."
        )
        user = (
            f"STYLE: {style}\n"
            "Rewrite the following text accordingly. Do not explain or comment.\n\n"
            f"<in>\n{text}\n</in>\n\n"
            "<out></out>"
        )
        prompt = self._apply_template(system, user)
        inputs = self.tok(prompt, return_tensors="pt").to(self.model.device)
        with torch.no_grad():
            out = self.model.generate(
                **inputs,
                max_new_tokens=max(64, len(text.split()) + 32),
                do_sample=True,
                top_p=0.9,
                temperature=0.8,
                repetition_penalty=1.05,
                eos_token_id=self.eos_id,
            )
        decoded = self.tok.decode(out[0], skip_special_tokens=True)
        return self._extract_xml(decoded)



class Similarity:
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def score(self, a: str, b: str) -> float:
        embs = self.model.encode([a, b], normalize_embeddings=True)
        return float(np.dot(embs[0], embs[1]))


# Optional: HF NER for extra protection around named entities (can be turned on if needed)
class HFNER:
    def __init__(self):
        self.pipe = pipeline("token-classification", model="dslim/bert-base-NER", aggregation_strategy="simple")

    def mark_entities(self, text: str) -> Tuple[str, Dict[str, str]]:
        mapping = {}
        out = self.pipe(text)
        # Sort by start index descending to avoid offset shifts
        out = sorted(out, key=lambda x: x["start"], reverse=True)
        t = text
        for ent in out:
            tok = f"{KEEP_PREFIX}{uuid.uuid4().hex[:8]}{KEEP_SUFFIX}"
            mapping[tok] = t[ent["start"]:ent["end"]]
            t = t[:ent["start"]] + tok + t[ent["end"]:]
        return t, mapping


# -----------------------------
# Paraphraser (Plan B)
# -----------------------------

class ParaphraserPlanB:
    def __init__(self, enable_ner=False, device=None):
        self.mt = MT(device=device)
        self.refiner = Refiner(device=device)
        self.sim = Similarity()
        self.ner = HFNER() if enable_ner else None

    def _translate_chain(self, s: str, pivots: List[str], cfg: DecodeCfg) -> str:
        # Source is English -> pivots -> English
        cur = s
        src = "en"
        for tgt in pivots:
            cur = self.mt.translate(cur, src_lang=src, tgt_lang=tgt, cfg=cfg)
            src = tgt
        cur = self.mt.translate(cur, src_lang=src, tgt_lang="en", cfg=cfg)
        return cur

    def _process_sentence(self, sent: str, level: int, style: str) -> str:
        # 1) Protect
        s = sent
        protected_s, mapping = protect_spans(s)
        if self.ner:
            protected_s, ner_map = self.ner.mark_entities(protected_s)
            mapping.update(ner_map)

        # Very short sentences: clamp paraphrase level
        eff_level = min(level, 2) if len(re.findall(r"\w+", sent)) < 8 else level

        pivots = choose_pivots(eff_level)
        cfg = decode_cfg_for_level(eff_level)

        # 2) MT pivot chain
        y = self._translate_chain(protected_s, pivots, cfg)

        # 3) Similarity gate (+ optional retry with gentler settings)
        sim_score = self.sim.score(protected_s, y)
        if sim_score < SIM_THRESH[eff_level]:
            # Retry once: soften decoding or shorten pivots
            alt_cfg = decode_cfg_for_level(max(1, eff_level - 1))
            alt_pivots = pivots[:-1] if len(pivots) > 1 else pivots
            y2 = self._translate_chain(protected_s, alt_pivots, alt_cfg)
            if self.sim.score(protected_s, y2) > sim_score:
                y = y2

        # 4) English refiner for fluency/style (keep placeholders intact)
        y = self.refiner.refine(y, style=style)

        # 5) Restore protected spans
        y = restore_spans(y, mapping)

        # 6) Diversity check (bigram overlap)
        ceil = BIGRAM_OVERLAP_CEIL.get(eff_level, 1.0)
        if ceil < 1.0 and bigram_overlap(sent, y) > ceil:
            # Nudge with a second tiny edit via refiner
            y = self.refiner.refine(
                f"Rewrite to reduce repeated phrasing vs the source.\nSOURCE:\n{sent}\nOUTPUT:\n{y}",
                style=style,
            )
            y = restore_spans(y, mapping)

        return y

    def paraphrase(
        self,
        text: str,
        level: int = 3,
        style: str = "neutral",
        sentencewise: bool = True,
    ) -> str:
        """
        level: 1..5 (higher = more divergence)
        style: "neutral" | "simpler" | "formal" | "concise" | etc.
        sentencewise: if True, split by sentences; else, process as one block
        """
        if not sentencewise:
            return self._process_sentence(text, level, style)

        sents = RE_SENT_SPLIT.split(text.strip())
        outs = [self._process_sentence(s, level, style) for s in sents if s.strip()]
        # Glue with a space that respects original punctuation spacing
        return re.sub(r"\s+", " ", " ".join(outs)).strip()


# -----------------------------
# Demo
# -----------------------------
if __name__ == "__main__":
    demo = r"""
        In Theorem 2, we show that $f(x)=\sum_{i=1}^n a_i x^i$ is strictly convex on $[0,1]$ when $a_i>0$.
        Consequently, $$f''(x)=\sum_{i=2}^n i(i-1)a_i x^{i-2} > 0$$ for all $x\in(0,1)$.
        See code below:
        ```python
        def f(x, a):
            return sum(a[i]*(x**i) for i in range(len(a)))
        The accuracy improved by 12.5% at 25 ms latency, according to https://example.com/paper
        .
        """
    para = ParaphraserPlanB(enable_ner=True)
    out = para.paraphrase(demo, level=3, style="concise", sentencewise=True)
    print("\n=== Paraphrase (PL=3, concise) ===\n")
    print(out)
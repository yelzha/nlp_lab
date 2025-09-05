import os
import glob
import shutil

def copy_files_by_pattern(source_pattern, dest_base_dir):
    """
    Finds files matching a glob pattern and copies them to a new base directory,
    maintaining the original subdirectory structure. If the destination file
    already exists, it is not replaced.

    Args:
        source_pattern (str): The glob pattern for the source files.
        dest_base_dir (str): The new base directory for the copied files.
    """
    # Use glob to find all files that match the source pattern.
    source_files = glob.glob(source_pattern, recursive=True)

    if not source_files:
        print(f"No files found matching the pattern: {source_pattern}")
        return

    # Extract the original base directory from the source pattern.
    # We assume the first directory in the pattern is the base directory.
    # E.g., from "experiments/...", we get "experiments".
    original_base_dir = source_pattern.split(os.path.sep)[0]

    for source_file in source_files:
        try:
            # Construct the destination path by replacing the original base directory
            # with the new destination base directory.
            # This preserves the entire subdirectory structure.
            dest_file = source_file.replace(original_base_dir, dest_base_dir)

            # Check if the destination file already exists.
            if os.path.exists(dest_file):
                print(f"Skipped '{source_file}' because '{dest_file}' already exists.")
                continue

            # Get the directory of the destination file.
            dest_dir = os.path.dirname(dest_file)

            # Create the destination directory if it doesn't exist.
            os.makedirs(dest_dir, exist_ok=True)

            # Copy the file. shutil.copy2 also copies metadata like timestamps.
            shutil.copy2(source_file, dest_file)
            print(f"Copied '{source_file}' to '{dest_file}'")
        except Exception as e:
            print(f"Error copying '{source_file}': {e}")


if __name__ == "__main__":
    # Define your source and destination paths.
    # Note: The glob patterns are passed as strings.
    # The `**` pattern is used for recursive searching across all subdirectories.
    source_base_dir = "../experiments"
    source_pattern = os.path.join(source_base_dir, "**", "gemma-3-12b-it", "**", "**", "**_agents_part_0.csv")

    dest_base_dir = "../view100"

    # Call the function to perform the copy operation.
    copy_files_by_pattern(source_pattern, dest_base_dir)

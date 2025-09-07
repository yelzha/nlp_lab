# This script generates a plot that visualizes the distribution of data
# points using a multi-layered, curved volume. The layers of the volume get
# progressively lighter as they move away from the mean, representing lower
# data density. A dashed line connects the means.

import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline

# --- 1. Define the data dynamically ---
# Store the data in a dictionary where the key is the x-point
# and the value is the corresponding y-data array.
data = {
    1: np.random.uniform(low=0.4, high=0.9, size=25),
    5: np.random.uniform(low=0.6, high=0.9, size=20),
    10: np.random.uniform(low=0.7, high=0.9, size=15),
    15: np.random.uniform(low=0.85, high=0.9, size=10),
    20: np.random.uniform(low=0.89, high=0.9, size=5),
    25: np.random.uniform(low=0.92, high=0.9, size=1)
}

print(data)

def plot_layered_volume(data_dict):
    """
    Generates a plot with a layered volume to visualize data distribution.

    Args:
        data_dict (dict): A dictionary where keys are x-points and values
                          are numpy arrays of y-data.
    """
    # Get a sorted list of the x-points from the provided dictionary
    x_points = sorted(data_dict.keys())

    # Calculate the mean of each batch of y-data.
    means = [np.mean(data_dict[x]) for x in x_points]

    # Define the percentile levels and corresponding darkness (alpha) values for the layers.
    # The innermost layer will be the darkest.
    percentile_levels = [
        (40, 60),  # Innermost layer, around the median
        (30, 70),
        (20, 80),
        (10, 90),
    ]
    alphas = [0.3, 0.2, 0.1, 0.05]

    # --- 2. Create the plot ---
    # Set up the plot figure and axes
    plt.figure(figsize=(10, 6))
    plt.style.use('seaborn-v0_8-whitegrid')

    # Plot the multi-layered volume dynamically
    for (lower_p, upper_p), alpha in zip(percentile_levels, alphas):
        # Calculate the percentile boundaries for each y-data set
        y_lower_points = [np.percentile(data_dict[x], lower_p) for x in x_points]
        y_upper_points = [np.percentile(data_dict[x], upper_p) for x in x_points]

        # Create smooth curved lines using splines
        x_curve = np.linspace(min(x_points), max(x_points), 200)

        # Use a spline degree of 3 for a smooth curve.
        # This requires at least 4 data points.
        if len(x_points) >= 4:
            spline_lower = make_interp_spline(x_points, y_lower_points, k=3)
            y_lower_curve = spline_lower(x_curve)

            spline_upper = make_interp_spline(x_points, y_upper_points, k=3)
            y_upper_curve = spline_upper(x_curve)

            # Fill the area between the curved lines
            plt.fill_between(
                x_curve,
                y_lower_curve,
                y_upper_curve,
                color='green',
                alpha=alpha,
            )
        else:
            # Fall back to a linear spline if there are not enough points
            spline_lower = make_interp_spline(x_points, y_lower_points, k=1)
            y_lower_curve = spline_lower(x_curve)

            spline_upper = make_interp_spline(x_points, y_upper_points, k=1)
            y_upper_curve = spline_upper(x_curve)

            plt.fill_between(
                x_curve,
                y_lower_curve,
                y_upper_curve,
                color='green',
                alpha=alpha,
            )


    # Plot a dashed line connecting the mean points

    # --- 3. Add labels, title, and a legend ---
    plt.title('Distribution of Y-Points with Layered Volume')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.xticks(x_points)  # Set x-ticks to be exactly at the data points
    plt.legend()
    plt.grid(True)
    plt.xlim(min(x_points) - 1, max(x_points) + 1)  # Adjust the x-axis limits
    plt.ylim(0.0, 1.0)  # Adjust the y-axis limits to focus on the data

    # --- 4. Display the plot ---
    plt.show()


# --- 5. Call the function with your data ---
plot_layered_volume(data)

import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# Monte Carlo Simulation Example
# Estimating Pi (π)
# -----------------------------

# Number of random points
N = 10000

# Generate random x and y coordinates
x = np.random.uniform(0, 1, N)
y = np.random.uniform(0, 1, N)

# Distance from origin
distance = x**2 + y**2

# Points inside quarter circle
inside_circle = distance <= 1

# Monte Carlo estimation of pi
pi_estimate = 4 * np.sum(inside_circle) / N

print(f"Estimated value of π: {pi_estimate}")
print(f"Actual value of π:    {np.pi}")

# -----------------------------
# Visualization
# -----------------------------

plt.figure(figsize=(8, 8))

# Points inside the circle
plt.scatter(
    x[inside_circle],
    y[inside_circle],
    s=2,
    label="Inside Circle"
)

# Points outside the circle
plt.scatter(
    x[~inside_circle],
    y[~inside_circle],
    s=2,
    label="Outside Circle"
)

plt.title(f"Monte Carlo Simulation for π\nEstimated π = {pi_estimate:.5f}")
plt.xlabel("x")
plt.ylabel("y")
plt.legend()
plt.axis("equal")

plt.show()

# -----------------------------
# Histogram of distances
# -----------------------------

plt.figure(figsize=(8, 5))

plt.hist(distance, bins=50)

plt.title("Histogram of Random Point Distances")
plt.xlabel("x² + y²")
plt.ylabel("Frequency")

plt.show()
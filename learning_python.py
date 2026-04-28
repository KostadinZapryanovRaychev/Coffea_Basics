import numpy as np

data = np.array([10, 20, 30, 40])
mask = np.array([True, False, True, False])

filtered = data[mask]
print(filtered)
import numpy as np
import awkward as ak
from coffea.nanoevents.methods import vector

# data = np.array([10, 20, 30, 40])
# mask = np.array([True, False, True, False])

# filtered = data[mask]

# events = np.array([
#     ["tau-_0"],
#     ["tau-_1"],
#     ["tau-_2"]
# ])

# print(events[:, 0])
# print(filtered)

# now the we create a vector with all its methods
# data = ak.zip(
#     {
#         "pt":  [10, 20, 30],
#         "eta": [0.1, 0.2, 0.3],
#         "phi": [0.0, 1.0, 2.0],
#         "mass":[0.5, 0.5, 0.5],
#     },
#     with_name="PtEtaPhiMLorentzVector",
#     behavior=vector.behavior,
# )

# print(data[0].delta_r(data[1]))

a = "Mitko"

def say_hello(name):
    print(f"Hello, {name}!")

def add_numbers(a, b):
    print(f"Adding {a} and {b}")
    return a + b
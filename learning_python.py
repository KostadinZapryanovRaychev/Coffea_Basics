import numpy as np
import awkward as ak
from pathlib import Path

import matplotlib.pyplot as plt
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


def make_dummy_histogram(output_dir: Path):
	"""Create a simple side-by-side histogram comparison from generated dummy data."""
	output_dir.mkdir(exist_ok=True)

	rng = np.random.default_rng(42)
	dummy_data = rng.normal(loc=0.0, scale=1.0, size=1000)
	bins_list = [10, 30, 70]

	fig, axes = plt.subplots(1, len(bins_list), figsize=(15, 4), sharey=True)
	for ax, bins in zip(axes, bins_list):
		ax.hist(dummy_data, bins=bins, color="tab:blue", alpha=0.75, edgecolor="black")
		ax.set_title(f"{bins} bins")
		ax.set_xlabel("Dummy value")
		ax.grid(alpha=0.2)

	axes[0].set_ylabel("Count")
	fig.suptitle("How Binning Changes a Histogram", fontsize=14)
	fig.tight_layout()

	out_path = output_dir / "dummy_histogram_bins_comparison.png"
	fig.savefig(out_path, dpi=150)
	plt.close(fig)
	print(f"Saved: {out_path}")


def main():
	here = Path(__file__).resolve().parent
	output_dir = here / "outputs"
	make_dummy_histogram(output_dir)


if __name__ == "__main__":
	main()


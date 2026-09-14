import uproot


def save_histograms(file_path, histograms):
    with uproot.recreate(file_path) as f:
        for name, h in histograms.items():
            f[name] = h

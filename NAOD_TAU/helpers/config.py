import json
from pathlib import Path

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[1] / "file_config.json"


def resolve_path(path, config_dir):
    if "://" in path or Path(path).is_absolute():
        return path
    return str((config_dir / path).resolve())


def load_config(config_path=DEFAULT_CONFIG_PATH):
    config_path = Path(config_path)
    with open(config_path) as f:
        config = json.load(f)

    for entry in config["root_files"]:
        entry["paths"] = [resolve_path(p, config_path.parent) for p in entry["paths"]]

    return config


def get_enabled_root_files(config):
    root_files = []
    for entry in config["root_files"]:
        if not entry.get("enabled", False):
            continue
        for path in entry["paths"]:
            root_files.append({"name": entry["name"], "path": path, "tree": entry["tree"]})

    return root_files

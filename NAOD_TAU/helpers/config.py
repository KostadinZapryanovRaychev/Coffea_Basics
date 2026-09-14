import json
from pathlib import Path

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[1] / "file_config.json"


def load_config(config_path=DEFAULT_CONFIG_PATH):
    config_path = Path(config_path)
    with open(config_path) as f:
        config = json.load(f)

    for root_file in config["root_files"]:
        path = Path(root_file["path"])
        if not path.is_absolute():
            root_file["path"] = str((config_path.parent / path).resolve())

    return config


def get_enabled_root_files(config):
    return [f for f in config["root_files"] if f.get("enabled", False)]

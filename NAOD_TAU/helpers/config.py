import json
from pathlib import Path

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[1] / "file_config.json"


def load_config(config_path=DEFAULT_CONFIG_PATH):
    with open(config_path) as f:
        return json.load(f)


def get_enabled_root_files(config):
    return [f for f in config["root_files"] if f.get("enabled", False)]

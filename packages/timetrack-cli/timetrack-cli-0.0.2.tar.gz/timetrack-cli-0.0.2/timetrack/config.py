import yaml
from pathlib import Path

def load_config(config_path: str) -> dict:
    """
    Load the YAML config file into a dictionary
    """
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"No config file '{config_path}' found.", 'red')
        raise FileNotFoundError

    return config

config_path = Path(__file__).parent / 'config.yml'
cfg = load_config(config_path)
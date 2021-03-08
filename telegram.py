import os
import yaml

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(ROOT_DIR, "config.yaml")

config = yaml.safe_load(open(CONFIG_PATH, encoding="utf8"))


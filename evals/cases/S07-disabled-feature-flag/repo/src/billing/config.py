import json
from pathlib import Path


FEATURE_FLAGS = json.loads(
    (Path(__file__).parents[2] / "config" / "features.json").read_text()
)

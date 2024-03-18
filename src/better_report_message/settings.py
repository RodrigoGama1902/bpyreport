import json
from pathlib import Path


class Settings:
    """Load the settings from the json file"""

    def __init__(self, json_path: Path):
        self.json_path = json_path
        self.data = json.load(open(json_path, "r", encoding="utf-8"))

    def basic(self, key: str):
        """Return the basic settings from the json file"""
        return self.data["basic"][key]

    def notification_draw(self, key: str):
        """Return the notification draw from the json file"""
        return self.data["notification_draw"][key]

    def colors(self, key: str):
        """Return the color from the json file"""
        return self.data["colors"][key]

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

import tomli_w

CONFIG_DIR = Path.home() / ".config" / "text-polisher"
CONFIG_FILE = CONFIG_DIR / "config.toml"


@dataclass
class Config:
    polish_hotkey: str = "<ctrl>+<shift>+p"
    dictate_hotkey: str = "<ctrl>+<shift>+d"
    language: str = "english"
    tone: str = "professional"
    whisper_model: str = "base"

    @classmethod
    def load(cls) -> "Config":
        config = cls()
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "rb") as f:
                data = tomllib.load(f)
            hotkeys = data.get("hotkeys", {})
            polish = data.get("polish", {})
            whisper = data.get("whisper", {})
            if "polish" in hotkeys:
                config.polish_hotkey = hotkeys["polish"]
            if "dictate" in hotkeys:
                config.dictate_hotkey = hotkeys["dictate"]
            if "language" in polish:
                config.language = polish["language"]
            if "tone" in polish:
                config.tone = polish["tone"]
            if "model" in whisper:
                config.whisper_model = whisper["model"]
        return config

    def save(self) -> None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        data = {
            "hotkeys": {
                "polish": self.polish_hotkey,
                "dictate": self.dictate_hotkey,
            },
            "polish": {
                "language": self.language,
                "tone": self.tone,
            },
            "whisper": {
                "model": self.whisper_model,
            },
        }
        with open(CONFIG_FILE, "wb") as f:
            tomli_w.dump(data, f)

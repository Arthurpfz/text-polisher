import os
from pathlib import Path

import rumps

ASSETS_DIR = Path(__file__).parent.parent / "assets"
LANGUAGES = ["English", "French", "German"]
TONES = ["Professional", "Friendly", "Informal", "Ironic"]


class MacOSTray(rumps.App):
    def __init__(self, config, on_language_change, on_tone_change, on_quit):
        icon_path = ASSETS_DIR / "icon.png"
        icon_arg = str(icon_path) if icon_path.exists() else None
        super().__init__("TP", icon=icon_arg, quit_button=None)
        self._config = config
        self._on_language_change = on_language_change
        self._on_tone_change = on_tone_change
        self._on_quit = on_quit
        rec_path = ASSETS_DIR / "icon_recording.png"
        self._recording_icon = str(rec_path) if rec_path.exists() else None
        self._normal_icon = icon_arg

        lang_items = [rumps.MenuItem(l, callback=self._set_lang) for l in LANGUAGES]
        tone_items = [rumps.MenuItem(t, callback=self._set_tone) for t in TONES]

        self.menu = [
            rumps.MenuItem("Language", lang_items),
            rumps.MenuItem("Tone", tone_items),
            None,
            rumps.MenuItem("Quit", callback=lambda _: self._on_quit()),
        ]
        self._update_checks()

    def _set_lang(self, sender):
        self._on_language_change(sender.title.lower())
        self._update_checks()

    def _set_tone(self, sender):
        self._on_tone_change(sender.title.lower())
        self._update_checks()

    def _update_checks(self):
        for item in self.menu["Language"].values():
            item.state = item.title.lower() == self._config.language
        for item in self.menu["Tone"].values():
            item.state = item.title.lower() == self._config.tone

    def set_status(self, status: str):
        if status == "recording":
            self.icon = self._recording_icon
            self.title = "\U0001F534"
        else:
            self.icon = self._normal_icon
            self.title = ""

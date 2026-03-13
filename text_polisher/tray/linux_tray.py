from pathlib import Path

from PIL import Image
import pystray
from pystray import MenuItem, Menu

ASSETS_DIR = Path(__file__).parent.parent / "assets"
LANGUAGES = ["English", "French", "German"]
TONES = ["Professional", "Friendly", "Informal", "Ironic"]


class LinuxTray:
    def __init__(self, config, on_language_change, on_tone_change, on_quit):
        self._config = config
        self._on_language_change = on_language_change
        self._on_tone_change = on_tone_change
        self._on_quit = on_quit
        self._normal_icon = Image.open(ASSETS_DIR / "icon.png")
        self._recording_icon = Image.open(ASSETS_DIR / "icon_recording.png")
        self._icon = None

    def _make_lang_action(self, lang):
        def action(icon, item):
            self._on_language_change(lang.lower())
            self._icon.update_menu()
        return action

    def _make_tone_action(self, tone):
        def action(icon, item):
            self._on_tone_change(tone.lower())
            self._icon.update_menu()
        return action

    def _is_lang(self, lang):
        return lambda item: self._config.language == lang.lower()

    def _is_tone(self, tone):
        return lambda item: self._config.tone == tone.lower()

    def _build_menu(self):
        lang_items = [
            MenuItem(l, self._make_lang_action(l), checked=self._is_lang(l))
            for l in LANGUAGES
        ]
        tone_items = [
            MenuItem(t, self._make_tone_action(t), checked=self._is_tone(t))
            for t in TONES
        ]
        return Menu(
            MenuItem("Language", Menu(*lang_items)),
            MenuItem("Tone", Menu(*tone_items)),
            Menu.SEPARATOR,
            MenuItem("Quit", lambda icon, item: self._on_quit()),
        )

    def run(self):
        self._icon = pystray.Icon(
            "text-polisher",
            self._normal_icon,
            "Text Polisher",
            menu=self._build_menu(),
        )
        self._icon.run()

    def set_status(self, status: str):
        if self._icon:
            if status == "recording":
                self._icon.icon = self._recording_icon
            else:
                self._icon.icon = self._normal_icon

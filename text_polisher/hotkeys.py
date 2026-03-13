import logging
import queue
from dataclasses import dataclass

from pynput import keyboard

logger = logging.getLogger("text_polisher")


@dataclass
class HotkeyEvent:
    type: str  # "polish" | "dictate_start" | "dictate_stop"


class HotkeyManager:
    def __init__(self, event_queue: queue.Queue, polish_hotkey: str, dictate_hotkey: str):
        self._queue = event_queue
        self._polish_hotkey = polish_hotkey
        self._dictate_hotkey = dictate_hotkey
        self._listener = None
        self._pressed: set = set()
        self._dictating = False
        self._polish_combo = self._parse_hotkey(polish_hotkey)
        self._dictate_combo = self._parse_hotkey(dictate_hotkey)

    @staticmethod
    def _parse_hotkey(hotkey_str: str) -> set:
        """Parse '<ctrl>+<shift>+p' into a set of pynput key references."""
        keys = set()
        for part in hotkey_str.lower().split("+"):
            part = part.strip().strip("<>")
            if part == "ctrl":
                keys.add(keyboard.Key.ctrl_l)
            elif part == "shift":
                keys.add(keyboard.Key.shift_l)
            elif part == "alt":
                keys.add(keyboard.Key.alt_l)
            elif part == "cmd":
                keys.add(keyboard.Key.cmd_l)
            elif len(part) == 1:
                keys.add(keyboard.KeyCode.from_char(part))
            else:
                keys.add(keyboard.KeyCode.from_char(part))
        return keys

    @staticmethod
    def _normalize(key) -> object:
        """Normalize left/right modifiers to left variant."""
        if key in (keyboard.Key.ctrl_r, keyboard.Key.ctrl_l, keyboard.Key.ctrl):
            return keyboard.Key.ctrl_l
        if key in (keyboard.Key.shift_r, keyboard.Key.shift_l, keyboard.Key.shift):
            return keyboard.Key.shift_l
        if key in (keyboard.Key.alt_r, keyboard.Key.alt_l, keyboard.Key.alt):
            return keyboard.Key.alt_l
        if key in (keyboard.Key.cmd_r, keyboard.Key.cmd_l, keyboard.Key.cmd):
            return keyboard.Key.cmd_l
        if hasattr(key, "char") and key.char:
            return keyboard.KeyCode.from_char(key.char.lower())
        return key

    def _combo_active(self, combo: set) -> bool:
        return combo.issubset(self._pressed)

    def _on_press(self, key):
        self._pressed.add(self._normalize(key))
        if self._combo_active(self._polish_combo):
            logger.info("Polish hotkey triggered")
            self._queue.put(HotkeyEvent(type="polish"))
            self._pressed.clear()
        elif not self._dictating and self._combo_active(self._dictate_combo):
            logger.info("Dictation started (hotkey held)")
            self._dictating = True
            self._queue.put(HotkeyEvent(type="dictate_start"))

    def _on_release(self, key):
        self._pressed.discard(self._normalize(key))
        if self._dictating and not self._combo_active(self._dictate_combo):
            logger.info("Dictation stopped (hotkey released)")
            self._dictating = False
            self._queue.put(HotkeyEvent(type="dictate_stop"))

    def start(self):
        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
        )
        self._listener.start()

    def stop(self):
        if self._listener:
            self._listener.stop()

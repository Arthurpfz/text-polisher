import platform
import subprocess
import time
import logging

from pynput.keyboard import Controller, Key

logger = logging.getLogger("text_polisher")

_IS_MAC = platform.system() == "Darwin"
_keyboard = Controller()


def copy_selection() -> str:
    """Simulate Cmd+C / Ctrl+C via pynput, then read clipboard."""
    modifier = Key.cmd if _IS_MAC else Key.ctrl
    _keyboard.press(modifier)
    _keyboard.press('c')
    _keyboard.release('c')
    _keyboard.release(modifier)

    time.sleep(0.2)

    if _IS_MAC:
        result = subprocess.run(["pbpaste"], capture_output=True, text=True, timeout=2)
    else:
        result = subprocess.run(
            ["xclip", "-selection", "clipboard", "-o"],
            capture_output=True, text=True, timeout=2,
        )
    return result.stdout


def paste_text(text: str) -> None:
    """Write text to clipboard, then simulate Cmd+V / Ctrl+V via pynput."""
    if _IS_MAC:
        subprocess.run(["pbcopy"], input=text, text=True, timeout=2, capture_output=True)
    else:
        subprocess.run(
            ["xclip", "-selection", "clipboard"],
            input=text, text=True, timeout=2, capture_output=True,
        )

    time.sleep(0.1)

    modifier = Key.cmd if _IS_MAC else Key.ctrl
    _keyboard.press(modifier)
    _keyboard.press('v')
    _keyboard.release('v')
    _keyboard.release(modifier)

import logging
import os
import queue
import signal
import sys
import threading

from dotenv import load_dotenv

from text_polisher.clipboard import copy_selection, paste_text
from text_polisher.config import CONFIG_DIR, Config
from text_polisher.hotkeys import HotkeyEvent, HotkeyManager
from text_polisher.polisher import Polisher

logger = logging.getLogger("text_polisher")

_tray = None


def _setup_logging():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = CONFIG_DIR / "polisher.log"
    handler = logging.FileHandler(log_file)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    root = logging.getLogger("text_polisher")
    root.addHandler(handler)
    root.setLevel(logging.INFO)


def _worker(event_queue: queue.Queue, polisher: Polisher, config: Config):
    """Worker thread: consumes hotkey events, does clipboard + API work."""
    while True:
        event: HotkeyEvent = event_queue.get()
        if event.type == "polish":
            try:
                text = copy_selection()
                if not text or not text.strip():
                    logger.info("No text selected, skipping")
                    continue
                logger.info("Polishing text (%d chars)", len(text))
                result = polisher.polish(text, config.language, config.tone)
                paste_text(result)
                logger.info("Polish complete, pasted (%d chars)", len(result))
            except Exception:
                logger.exception("Error during polish")
        elif event.type == "dictate_start":
            logger.info("Dictation event received (V3 feature)")
        elif event.type == "dictate_stop":
            logger.info("Dictation stop event received (V3 feature)")


def run():
    global _tray
    load_dotenv()
    _setup_logging()
    logger.info("Text Polisher starting")

    config = Config.load()

    try:
        polisher = Polisher()
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    event_queue: queue.Queue[HotkeyEvent] = queue.Queue()

    worker_thread = threading.Thread(
        target=_worker, args=(event_queue, polisher, config), daemon=True
    )
    worker_thread.start()

    hotkey_mgr = HotkeyManager(event_queue, config.polish_hotkey, config.dictate_hotkey)
    hotkey_mgr.start()

    logger.info("Listening for hotkeys (polish: %s)", config.polish_hotkey)
    print(f"Text Polisher running. Press {config.polish_hotkey} to polish selected text.")

    def on_language_change(lang):
        config.language = lang
        config.save()
        logger.info("Language changed to %s", lang)

    def on_tone_change(tone):
        config.tone = tone
        config.save()
        logger.info("Tone changed to %s", tone)

    def on_quit():
        hotkey_mgr.stop()
        logger.info("Text Polisher stopped via tray")
        os._exit(0)

    # Try to start tray (V2+)
    try:
        from text_polisher.tray import create_tray
        _tray = create_tray(config, on_language_change, on_tone_change, on_quit)
    except ImportError:
        _tray = None

    if _tray:
        logger.info("Tray icon started")
        print("Tray icon active. Use it to change language/tone.")
        _tray.run()  # blocks main thread
    else:
        # Fallback: no tray, just wait
        print("Press Ctrl+C to quit.")
        stop_event = threading.Event()
        signal.signal(signal.SIGINT, lambda *_: stop_event.set())
        signal.signal(signal.SIGTERM, lambda *_: stop_event.set())
        try:
            stop_event.wait()
        finally:
            hotkey_mgr.stop()
            logger.info("Text Polisher stopped")
            print("\nText Polisher stopped.")

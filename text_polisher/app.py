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


def _setup_logging():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = CONFIG_DIR / "polisher.log"
    handler = logging.FileHandler(log_file)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    root = logging.getLogger("text_polisher")
    root.addHandler(handler)
    root.setLevel(logging.INFO)


class _AppState:
    """Mutable state shared between threads."""
    def __init__(self):
        self.recorder = None
        self.transcriber = None
        self.indicator = None
        self.tray = None


def _worker(event_queue: queue.Queue, polisher: Polisher, config: Config, state: _AppState):
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
            if state.recorder:
                try:
                    if state.indicator:
                        state.indicator.show()
                    state.recorder.start()
                except Exception:
                    logger.exception("Error starting dictation")
                    if state.indicator:
                        state.indicator.hide()
        elif event.type == "dictate_stop":
            if state.recorder and state.transcriber:
                try:
                    audio = state.recorder.stop()
                    if state.indicator:
                        state.indicator.hide()
                    if len(audio) < state.recorder.samplerate * 0.3:
                        logger.info("Recording too short, skipping")
                        continue
                    text = state.transcriber.transcribe(audio)
                    if not text.strip():
                        logger.info("Transcription empty, skipping")
                        continue
                    logger.info("Dictation transcribed, polishing")
                    result = polisher.polish(text, config.language, config.tone)
                    paste_text(result)
                    logger.info("Dictation polish complete")
                except Exception:
                    logger.exception("Error during dictation")
                    if state.indicator:
                        state.indicator.hide()


def run():
    load_dotenv(CONFIG_DIR / ".env")
    load_dotenv()  # also check cwd
    _setup_logging()
    logger.info("Text Polisher starting")

    config = Config.load()

    try:
        polisher = Polisher()
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    event_queue: queue.Queue[HotkeyEvent] = queue.Queue()
    state = _AppState()

    # Initialize dictation components (V3)
    try:
        from text_polisher.dictation.recorder import Recorder
        from text_polisher.dictation.transcriber import Transcriber
        state.recorder = Recorder()
        state.transcriber = Transcriber(config.whisper_model)
        logger.info("Dictation available (Whisper model: %s)", config.whisper_model)
        print(f"Dictation available. Hold {config.dictate_hotkey} to dictate.")
    except ImportError:
        logger.info("Dictation dependencies not installed, skipping")

    worker_thread = threading.Thread(
        target=_worker, args=(event_queue, polisher, config, state), daemon=True,
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
        state.tray = create_tray(config, on_language_change, on_tone_change, on_quit)
    except ImportError:
        state.tray = None

    # Wire recording indicator to tray
    if state.recorder:
        from text_polisher.dictation.indicator import RecordingIndicator
        state.indicator = RecordingIndicator(state.tray)

    if state.tray:
        logger.info("Tray icon started")
        print("Tray icon active. Use it to change language/tone.")
        state.tray.run()  # blocks main thread
    else:
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

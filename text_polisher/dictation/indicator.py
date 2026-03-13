import logging

logger = logging.getLogger("text_polisher")


class RecordingIndicator:
    def __init__(self, tray=None):
        self._tray = tray

    def show(self):
        logger.info("Recording indicator: ON")
        if self._tray and hasattr(self._tray, "set_status"):
            self._tray.set_status("recording")

    def hide(self):
        logger.info("Recording indicator: OFF")
        if self._tray and hasattr(self._tray, "set_status"):
            self._tray.set_status("idle")

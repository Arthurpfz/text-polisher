import logging

import numpy as np
import sounddevice as sd

logger = logging.getLogger("text_polisher")


class Recorder:
    def __init__(self, samplerate: int = 16000):
        self._sr = samplerate
        self._frames: list[np.ndarray] = []
        self._stream = None

    def start(self):
        self._frames = []
        self._stream = sd.InputStream(
            samplerate=self._sr, channels=1, dtype="float32",
            callback=self._callback,
        )
        self._stream.start()
        logger.info("Recording started")

    def _callback(self, indata, frames, time, status):
        if status:
            logger.warning("Audio status: %s", status)
        self._frames.append(indata.copy())

    def stop(self) -> np.ndarray:
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        if not self._frames:
            return np.array([], dtype=np.float32)
        audio = np.concatenate(self._frames, axis=0).flatten()
        duration = len(audio) / self._sr
        logger.info("Recording stopped (%.1fs audio)", duration)
        return audio

    @property
    def samplerate(self) -> int:
        return self._sr

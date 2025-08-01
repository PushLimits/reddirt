"""Text-to-speech service for Reddit Who Dis."""

import logging
import queue
import threading

import numpy as np
import requests
import sounddevice as sd


class TTSService:
    """Service for synthesizing speech from text."""

    def __init__(self, default_voice: str = "am_adam(1)+af_heart(3)"):
        """Initialize the TTS service."""
        self.default_voice = default_voice
        self.api_url = "https://api.kokoro-fastapi.com/v1/tts/stream"

    def _get_headers(self) -> dict:
        """Get API headers."""
        return {"Accept": "application/json", "Content-Type": "application/json"}

    def _get_payload(self, text: str, voice: str) -> dict:
        """Get API payload."""
        return {
            "text": text,
            "voice": voice,
            "speed": 1.0,
            "emotion": "Neutral",
            "language": "en",
        }

    def _stream_audio(self, text: str, voice: str):
        """Stream audio from the TTS API and play it."""
        audio_queue = queue.Queue()
        stop_event = threading.Event()

        def fetch_audio():
            try:
                with requests.post(
                    self.api_url,
                    headers=self._get_headers(),
                    json=self._get_payload(text, voice),
                    stream=True,
                ) as response:
                    response.raise_for_status()
                    for chunk in response.iter_content(chunk_size=4096):
                        audio_queue.put(chunk)
            except requests.RequestException as e:
                logging.error(f"Error fetching audio stream: {e}")
            finally:
                audio_queue.put(None)  # Signal end of stream

        def play_audio():
            try:
                with sd.OutputStream(samplerate=24000, channels=1, dtype="float32") as stream:
                    while not stop_event.is_set():
                        chunk = audio_queue.get()
                        if chunk is None:
                            break
                        audio_data = np.frombuffer(chunk, dtype=np.float32)
                        stream.write(audio_data)
            except Exception as e:
                logging.error(f"Error playing audio: {e}")

        fetch_thread = threading.Thread(target=fetch_audio)
        play_thread = threading.Thread(target=play_audio)

        fetch_thread.start()
        play_thread.start()

        fetch_thread.join()
        play_thread.join()

    def synthesize_speech(self, text: str, voice: str = None, stream: bool = True):
        """Synthesize speech from text.

        Args:
            text: Text to synthesize.
            voice: Voice to use for synthesis.
            stream: Whether to stream the audio.
        """
        if not text:
            logging.warning("No text provided for TTS synthesis.")
            return

        voice = voice or self.default_voice

        if stream:
            self._stream_audio(text, voice)
        else:
            logging.error("Non-streaming TTS not implemented.")

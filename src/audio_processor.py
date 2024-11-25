from typing import List
import os
import subprocess
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError
import time


class AudioProcessor:
    def __init__(self, chunk_duration: int = 10 * 60 * 1000):
        self.chunk_duration = chunk_duration  # 10 minutes in milliseconds
        self._check_ffmpeg()

    def _check_ffmpeg(self):
        """Check if ffmpeg is available"""
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True)
        except FileNotFoundError:
            raise RuntimeError(
                "ffmpeg is not installed. Please install ffmpeg to process audio files."
            )

    def split_audio(self, audio_path: str) -> List[str]:
        """Split audio file into chunks"""
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        try:
            audio = AudioSegment.from_mp3(audio_path)
            chunks = []

            ts = int(time.time() * 1000)
            chunks_path = f"/tmp/chunks_{ts}"
            print(f"Storing chunks in {chunks_path}...")
            os.makedirs(chunks_path, exist_ok=True)

            for i in range(0, len(audio), self.chunk_duration):
                chunk = audio[i : i + self.chunk_duration]
                chunk_path = f"{chunks_path}/chunk_{i//self.chunk_duration}.mp3"
                chunk.export(chunk_path, format="mp3")
                chunks.append(chunk_path)

            print(f"Split audio into {len(chunks)} chunks")
            return chunks

        except CouldntDecodeError:
            raise RuntimeError(
                "Failed to decode audio file. Please ensure it's a valid MP3 file."
            )
        except Exception as e:
            raise RuntimeError(f"Error splitting audio: {str(e)}")

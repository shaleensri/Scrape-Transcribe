from abc import ABC, abstractmethod
from pathlib import Path

class Transcriber(ABC):
    @abstractmethod
    def transcribe(self, video_path: Path) -> str:
        """Transcribe a video file and return the text"""
        pass

from pathlib import Path
from faster_whisper import WhisperModel
from transcriber.whisper_wrapper import WhisperTranscriber

class WhisperTranscriber(Transcriber):
    def __init__(self, model_size: str = "base", compute_type: str = "float32"):
        """
        model_size: one of ["tiny", "base", "small", "medium", "large"]
        better model for gpu - "small", "medium", "large"
        better compute for gpu - "float 16" or "auto"
        compute_type: "int8", "int8_float16", "float16", "float32", "auto"

        i went with "base" as the best trade-off for speed and accuraccy. 
        might mess with background noise and heavy accents: dont think that'll be a problem for michigan lol
        """
        self.model = WhisperModel(model_size, compute_type=compute_type)

    def transcribe(self, video_path: Path) -> str:
        segments, _ = self.model.transcribe(str(video_path))

        transcript = ""
        for segment in segments:
            print(f"[{segment.start:.2f} - {segment.end:.2f}] {segment.text.strip()}")
            transcript += f"{segment.text.strip()} "

        return transcript.strip()

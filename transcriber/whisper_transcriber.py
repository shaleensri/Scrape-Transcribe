from pathlib import Path
from faster_whisper import WhisperModel
from transcriber.transcriber import Transcriber

class WhisperTranscriber(Transcriber):
    def __init__(self, model_size: str = "base", compute_type: str = "float32"):
        """
        model_size: one of ["tiny", "base", "small", "medium", "large"]
        better model for gpu - "small", "medium", "large"
        better compute for gpu - "float 16" or "auto"
        compute_type: "int8", "int8_float16", "float16", "float32", "auto"

        i went with "base" as the best trade-off for speed and accuraccy. 
        might mess with background noise and heavy accents: 
        dont think that'll be a problem for michigan lol
        """
        self.model = WhisperModel(model_size, compute_type=compute_type)

    def transcribe(self, video_path: Path) -> str:
        """
        Transcribe the audio from a video file using faster_whisper.
        Prints in segments with start and end times.
        Returns the path to the transcript file.
        """
        segments, _ = self.model.transcribe(str(video_path))

        transcript_path = video_path.with_suffix(".txt")
        with open(transcript_path, "w") as f:
            for segment in segments:
                start = f"{segment.start:.2f}"
                end = f"{segment.end:.2f}"
                text = segment.text.strip()

                # Write in [start - end] format into file
                f.write(f"[{start} - {end}] {text}\n")

        return transcript_path

    def transcribe_test(self, video_path: Path) -> str:
        """ 
        Test transcription method for testing purposes.
        """
        transcript_path = video_path.with_suffix(".txt")
        with open(transcript_path, "w") as f:
            f.write("This is a test transcription.\n")
            f.write("It is not real data, just a placeholder.\n")
        return transcript_path
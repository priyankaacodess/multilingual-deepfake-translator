import shutil
import subprocess
from pathlib import Path


class Wav2LipError(RuntimeError):
    pass


class Wav2LipSync:
    def __init__(self, repo_path: Path, checkpoint_path: Path, python_bin: str = "python") -> None:
        self._repo_path = repo_path
        self._checkpoint_path = checkpoint_path
        self._python_bin = python_bin

    def generate(self, source_video: Path, synthesized_audio: Path, output_video: Path) -> None:
        output_video.parent.mkdir(parents=True, exist_ok=True)
        command = [
            self._python_bin,
            str(self._repo_path / "inference.py"),
            "--checkpoint_path",
            str(self._checkpoint_path),
            "--face",
            str(source_video),
            "--audio",
            str(synthesized_audio),
            "--outfile",
            str(output_video),
        ]
        completed = subprocess.run(command, capture_output=True, text=True)
        if completed.returncode != 0:
            raise Wav2LipError(completed.stderr.strip() or "Wav2Lip inference failed")


class MockLipSync:
    def generate(self, source_video: Path, synthesized_audio: Path, output_video: Path) -> None:
        output_video.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_video, output_video)

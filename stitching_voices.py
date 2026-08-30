from pathlib import Path
from typing import Iterable
from pydub import AudioSegment


def stitch_audio_files(
    files: Iterable[str | Path],
    output_file: str | Path,
    silence_ms: int = 150,
    target_sample_rate: int = 24_000,
    target_channels: int = 1,
) -> Path:
    """
    Concatenate audio files into a single output file.

    Parameters
    ----------
    files:
        Ordered iterable of audio file paths.
    output_file:
        Destination path, such as "combined.wav" or "combined.ogg".
    silence_ms:
        Silence inserted between clips.
    target_sample_rate:
        Output sample rate.
    target_channels:
        1 for mono, 2 for stereo.
    """
    file_paths = [Path(file) for file in files]

    if not file_paths:
        raise ValueError("No audio files were provided.")

    missing_files = [path for path in file_paths if not path.is_file()]
    if missing_files:
        missing = "\n".join(str(path) for path in missing_files)
        raise FileNotFoundError(f"These files do not exist:\n{missing}")

    separator = AudioSegment.silent(
        duration=silence_ms,
        frame_rate=target_sample_rate,
    )

    combined = AudioSegment.empty()

    for index, path in enumerate(file_paths):
        print(f"Loading: {path}")

        clip = AudioSegment.from_file(path)
        clip = clip.set_frame_rate(target_sample_rate)
        clip = clip.set_channels(target_channels)

        if index > 0 and silence_ms > 0:
            combined += separator

        combined += clip

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_format = output_path.suffix.lower().lstrip(".")
    if not output_format:
        raise ValueError("The output filename must have an extension.")

    export_parameters = {}

    if output_format == "ogg":
        export_parameters["codec"] = "libvorbis"

    combined.export(
        output_path,
        format=output_format,
        **export_parameters,
    )

    print(f"Saved combined audio to: {output_path}")
    print(f"Duration: {len(combined) / 1000:.2f} seconds")

    return output_path

if __name__ == "__main__":
    folder = Path(r"AI-ssistant/models/voices/Marcus_voices_split")

    ogg_files = sorted(folder.glob("*.ogg"))

    stitch_audio_files(
        files=ogg_files,
        output_file=folder / "combined.wav",
        silence_ms=0,
    )
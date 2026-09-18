import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

import yaml

CONFIG_YAML = Path("/data/config/config.yaml")
DOWNLOADS_DIR = Path("/data/downloads")
ENCODED_DIR = Path("/data/encoded")

def load_config() -> dict:
    with open(CONFIG_YAML) as f:
        return yaml.safe_load(f)


def url_hash(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()[:16]


def download(url: str, output_dir: Path, headers: dict) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    name = url_hash(url)
    dest = output_dir / f"{name}.mp4"

    header_args = []
    for key, value in headers.items():
        header_args += ["-headers", f"{key}: {value}"]

    cmd = [
        "ffmpeg",
        "-y",
        "-loglevel", "error",
        *header_args,
        "-i", url,
        "-c", "copy",
        str(dest),
    ]

    if dest.exists():
        print(f"Skip: {dest}")
        return dest

    print(f"Downloading: {url}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        dest.unlink(missing_ok=True)
        print(f"Failed: {url}", file=sys.stderr)
    else:
        print(f"Saved: {dest}")
    return dest


def rename(src: Path, name: str) -> None:
    dest = src.parent / f"{name}.mp4"
    if dest.exists():
        print(f"Skip rename: {dest}")
        return
    src.rename(dest)
    src.touch()
    print(f"Renamed: {dest}")


def encode(src: Path, output_dir: Path, crf: int) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    dest = output_dir / src.name

    cmd = [
        "ffmpeg",
        "-y", "-nostdin",
        "-hwaccel", "qsv",
        "-hwaccel_output_format", "qsv",
        "-loglevel", "error",
        "-i", str(src),
        "-c:v", "h264_qsv",
        "-global_quality", str(crf),
        "-c:a", "copy",
        str(dest),
    ]

    print(f"Encoding: {src.name}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"Encode failed: {src.name}", file=sys.stderr)
    else:
        print(f"Encoded: {dest}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Download videos defined in config.yaml")
    parser.add_argument("--encode", action="store_true", help="Re-encode downloaded videos with libx264")
    args = parser.parse_args()

    config = load_config()
    headers = config.get("headers", {})

    for video in config["videos"]:
        src = download(video["url"], DOWNLOADS_DIR, headers)

        if args.encode:
            if not src.exists():
                print(f"Missing: {src}", file=sys.stderr)
                continue
            encode(src, ENCODED_DIR, 23)
            rename(ENCODED_DIR / src.name, video["name"])


if __name__ == "__main__":
    main()

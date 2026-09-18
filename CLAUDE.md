# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Build and deploy to remote host
task build

# Copy config.yaml to deploy target and run
task run

# Run interactively in dev container
docker compose run --rm dev python main.py --encode
```

## Architecture

A single Python script (`app/main.py`) handles all logic.

**Execution flow:**
1. Load `/data/config/config.yaml`
2. Download each video via ffmpeg with `config.headers` passed as `-headers` → `/data/downloads/<sha256[:16]>.mp4`
3. If `--encode` is given, re-encode with Intel QSV (`h264_qsv`) → `/data/encoded/`, then rename using `config.videos[].name`

**Docker:**
- `app/Dockerfile` — production. Ubuntu 24.04, Intel QSV for 9th-gen CPUs (`libmfx1` + `libvpl2` + `intel-media-va-driver-non-free`), `LIBVA_DRIVER_NAME=iHD`
- `app/Dockerfile.dev` — development. `python:3.14-slim`, no QSV
- The `dev` service in `compose.yaml` mounts `./app` and `./data`

**Deploy target:** Runs as `docker compose run --rm video_utils` on `DEPLOY_HOST`. Built for linux/amd64 via `AMD64_BUILDER` and pushed to `REGISTRY`.

## config.yaml

Schema for `/data/config/config.yaml`:

```yaml
headers:
  User-Agent: "..."   # HTTP headers passed to ffmpeg
videos:
  - name: "output filename"
    url: "https://..."
```

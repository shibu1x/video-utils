FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    libva-drm2 \
    intel-media-va-driver-non-free \
    libmfx1 \
    libvpl2 \
    ffmpeg \
    python3 \
    python3-pip \
    python-is-python3 \
    && rm -rf /var/lib/apt/lists/*

ENV LIBVA_DRIVER_NAME=iHD

# Copy requirements and install Python dependencies
WORKDIR /app
COPY requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt --break-system-packages

COPY . .

RUN python -m compileall -f .

ENTRYPOINT ["python", "main.py"]

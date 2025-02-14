FROM python:3.13-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

FROM python:3.13-slim

WORKDIR /app

ENV PMRS_CONFIG_DIR=/app/data
ENV PMRS_LOG_DIR=/app/data
ENV FORCE_COLOR=1
ENV PYTHONUNBUFFERED=1

COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages

COPY src/plex_music_ratings_sync /app/plex_music_ratings_sync

RUN echo '#!/bin/sh\nexec python -u -m plex_music_ratings_sync "$@"' > /usr/local/bin/plex-music-ratings-sync && \
    chmod +x /usr/local/bin/plex-music-ratings-sync

RUN echo '#!/bin/sh\nexec python -u -m plex_music_ratings_sync "$@"' > /usr/local/bin/pmrs && \
    chmod +x /usr/local/bin/pmrs

ENTRYPOINT ["plex-music-ratings-sync"]

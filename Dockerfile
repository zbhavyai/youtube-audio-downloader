FROM python:3.11-slim
LABEL org.opencontainers.image.title="youtube-audio-downloader"
LABEL org.opencontainers.image.description="YouTube Audio Downloader"
LABEL org.opencontainers.image.source="https://github.com/zbhavyai/youtube-audio-downloader"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.authors="Bhavyai Gupta <https://zbhavyai.github.io>"
LABEL org.opencontainers.image.version="1.0.0"
WORKDIR /app
COPY requirements.txt .
COPY src /app/src
COPY samples /app/samples
RUN pip install --no-cache-dir --requirement requirements.txt
ENTRYPOINT ["python", "-m", "src"]
CMD []

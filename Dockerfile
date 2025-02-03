FROM python:3.11-slim
LABEL maintainer="https://zbhavyai.github.io"
LABEL repo="https://github.com/zbhavyai/youtube-audio-downloader"
WORKDIR /app
COPY requirements.txt .
COPY *py .
COPY *csv .
RUN pip install --no-cache-dir --requirement requirements.txt
ENTRYPOINT ["python", "script.py"]
CMD []

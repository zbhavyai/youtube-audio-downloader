# YouTube Audio Downloader

### Setup

1. Install dependencies

   ```bash
   pip install --requirement requirements.txt
   ```

2. Print the contents of the CSV file

   ```bash
   ./script.py --csv sample.csv
   ```

### Running with Docker

1. Build the docker image

   ```bash
   docker build --tag youtube-audio-downloader:1.0.0 .
   ```

2. Run the docker container

   ```bash
   docker container run --volume $(pwd):/app/output --rm youtube-audio-downloader:1.0.0 --csv sample.csv
   ```

# YouTube Audio Downloader

### Setup

1. Install dependencies

   ```shell
   pip install --requirement requirements.txt
   ```

2. Print the contents of the CSV file

   ```shell
   ./script.py --csv sample.csv
   ```

3. Downloading a single audio

   ```shell
   ./script.py --url https://www.youtube.com/watch?v=5qap5aO4i9A --filename sample.mp3
   ```

### Running with Docker

1. Build the docker image

   ```shell
   docker build --tag youtube-audio-downloader:1.0.0 .
   ```

2. Print the contents of the CSV file

   ```shell
   docker container run --volume $(pwd):/app/output --rm youtube-audio-downloader:1.0.0 --csv sample.csv
   ```

3. Downloading a single audio

   ```shell
   docker container run --volume $(pwd):/app/output --rm youtube-audio-downloader:1.0.0 --url https://www.youtube.com/watch?v=5qap5aO4i9A --filename sample.mp3
   ```

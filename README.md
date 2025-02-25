# YouTube Audio Downloader

### Setup

1. Install dependencies

   ```shell
   pip install --requirement requirements.txt
   ```

2. Print the contents of the CSV file

   ```shell
   python -m src --csv samples/data.csv --testcsv
   ```

3. Downloading audios from CSV

   ```shell
   python -m src --csv samples/data.csv --download
   ```

4. Downloading a single audio

   ```shell
   python -m src --url https://www.youtube.com/watch?v=D9G1VOjN_84 --filename enemy
   ```

### Running with Docker

1. Build the docker image

   ```shell
   docker build --tag youtube-audio-downloader:1.0.0 .
   ```

2. Print the contents of the CSV file

   ```shell
   docker container run --volume $(pwd):/app/output --rm youtube-audio-downloader:1.0.0 --csv samples/data.csv --testcsv
   ```

3. Downloading audios from CSV

   ```shell
   docker container run --volume $(pwd):/app/output --rm youtube-audio-downloader:1.0.0 --csv samples/data.csv --download
   ```

4. Downloading a single audio

   ```shell
   docker container run --volume $(pwd)/output:/app/output --rm youtube-audio-downloader:1.0.0 --url https://www.youtube.com/watch?v=D9G1VOjN_84 --filename enemy
   ```

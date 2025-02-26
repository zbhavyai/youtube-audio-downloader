# YouTube Audio Downloader

A python script to download and manage metadata for YouTube audio files. The script supports individual file operations and batch processing via a CSV file.

## Features

- **Metadata Management**: Print, clean, and set ID3 tags.
- **YouTube Audio Download**: Download audio from a YouTube URL.
- **CSV Processing**: Perform bulk operations based on a CSV file.

## Installation

1. Clone the repository

2. Install dependencies

   ```shell
   pip install -r requirements.txt
   ```

3. Print the version

   ```shell
   python -m src version
   ```

## Usage

Run the script using

```shell
python -m src <group> <action> [options]
```

### Command Groups & Actions

#### 1. Metadata Operations

```shell
python -m src metadata --print --file <FILE_OR_DIRECTORY>

python -m src metadata --clean --file <FILE_OR_DIRECTORY>

python -m src metadata --set --file <FILE_OR_DIRECTORY> \
    --title <TITLE> \
    --artist <ARTIST> \
    --year <YEAR> \
    --composer <COMPOSER> \
    --comment <COMMENT> \
    --genre <GENRE> \
    --album <ALBUM>
```

#### 2. Download Audio from YouTube

```shell
python -m src download --url <YOUTUBE_URL> --output <OUTPUT_FILE>
```

#### 3. CSV Processing

```shell
python -m src csv --file <CSV_FILE> --print
python -m src csv --file <CSV_FILE> --download
```

## Running with Docker

A Dockerfile is provided for containerized execution. Build and run the image:

```shell
docker build --tag youtube-audio-downloader:1.0.0 .
docker container run --rm --volume $(pwd):/app/output youtube-audio-downloader:1.0.0 <group> <action> [options]
```

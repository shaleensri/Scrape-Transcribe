# State Affairs Legislature Video Scraper & Transcriber Project

## Overview

This project automates the **scraping, downloading, transcription, and (optionally) cloud upload** of legislative session videos from:

- **Michigan House** Video Archive
- **Michigan Senate** Video Archive

The system can:

- Periodically scrape new videos
- Download them locally or to cloud storage
- Transcribe them using **Whisper** via `faster-whisper`
- Store and/or upload both video and transcript to **Google Cloud Storage**
- Run continuously on a **configurable schedule** in demo or production mode

Access the GCP Bucket with all the files stored here via API: https://storage.googleapis.com/legislature-videos-shaleen (Made public for the time being)

---

## Features

### 1. **House Scraper**

- Extracts video metadata from the House archive webpage
- Downloads `.mp4` videos from direct URLs via ffmpeg

### 2. **Senate Scraper**

- Uses the Senate API (`/api/all`) to fetch full video listings
- Parses committee names, recording dates, and video IDs
- Generates the correct `.m3u8` URL for each video
- Downloads videos via `ffmpeg` from HLS streams

### 3. **Processing Pipeline**

- Skips already processed videos (based on `state.json` in cloud mode or local file checks in local mode)
- Downloads video
- Transcribes using **Whisper**
- Uploads video & transcript to **Google Cloud Storage** (optional)
- Cleans up local storage (optional in cloud mode)

### 4. **Multi-threaded Execution**

- Runs **House** and **Senate** pipelines **in parallel** for efficiency

### 5. **Scheduler**

- Runs at configurable intervals
- Prevents overlapping runs using a lock file (Waits for a previous run to finish)
- First run starts immediately
- Easily configurable for **demo** (frequent runs) or **production** (less frequent runs)

---

##  Project Structure

main.py -  Runs House and Senate pipelines in parallel

scheduler.py - Timed job runner with parallel pipelines

### fetcher/
base_scraper.py

house_scraper_static.py - House metadata scraper

senate_scraper.py - Senate metadata scraper

### storage/
file_manager.py -  Download functions (House: direct MP4, Senate: HLS via ffmpeg)

state_tracker.py -  Processed state tracking (cloud mode)

video_processor.py -  process_video() pipeline

### transcriber/

whisper_transcriber.py - Whisper transcription wrapper

---

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/shaleensri/Scrape-Transcribe.git
```
### 2. Create a Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt

brew install ffmpeg # mac
```

## Usage

#### Option 1. Run Once (Multi-threaded)
```bash
python main.py # Runs both House and Senate pipelines in parallel for the given limit in main.py. 
```

#### Option 2. Run with Scheduler (Also multi-threaded)
```bash
python scheduler.py
```
- Adjust in scheduler.py:
```python
FREQ_MINUTES = 5 # Frequency in minutes

VIDEO_LIMIT = 2 # Videos per run
```


***Developed by Shaleen Srivastava***

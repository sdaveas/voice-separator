# Voice Separator

Separate vocals and melody from your audio files with AI.

## Features
- Upload an audio file or provide a YouTube link
- Select a segment to process (optional)
- Separate vocals and melody using Demucs
- Download separated tracks (vocals, melody, original)

## Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd voice-separator
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install FFmpeg:**
   - **macOS:** `brew install ffmpeg`
   - **Ubuntu/Debian:** `sudo apt-get install ffmpeg`
   - **Windows:** [Download from ffmpeg.org](https://ffmpeg.org/download.html)

## Usage

Run the Streamlit app locally:

```bash
streamlit run app/app.py
```

- Open the provided local URL in your browser.
- Upload an audio file or paste a YouTube link.
- Optionally select a segment to process.
- Click **Separate** to process the audio.
- Download the separated tracks as needed.

## Requirements

- Python 3.8+
- The following Python packages (see `requirements.txt`):
  - torch>=2.0.0
  - demucs>=4.0.0
  - ffmpeg-python>=0.2.0
  - soundfile>=0.12.1
  - diffq>=0.2.0
  - streamlit>=1.32.0
  - yt-dlp>=2024.4.9
  - numpy>=1.26.4
- FFmpeg (system package, see above)

---

Made with ❤️ using Streamlit and Demucs

[☕ Buy Me a Coffee](https://buymeacoffee.com/br3gan) 

def download_youtube_audio(yt_url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'temp_audio.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
        }],
        'cookiefile': 'cookies.txt',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(yt_url, download=True)
        temp_audio_path = ydl.prepare_filename(info).replace(info['ext'], 'wav')
        base_name = info.get('title', 'yt_audio')
    return temp_audio_path, base_name 
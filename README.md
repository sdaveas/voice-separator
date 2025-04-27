# Voice Separator

A web app to separate vocals and melody from your audio files using AI (Demucs) and Streamlit.

## Features
- Upload an audio file (WAV, MP3, M4A, FLAC)
- Get separate tracks for vocals and melody
- Download the separated tracks
- Powered by Demucs and Streamlit

## Local Development

### Using pip
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the app locally:**
   ```bash
   streamlit run app/app.py
   ```
   The app will be available at [http://localhost:8501](http://localhost:8501)

### Using pipenv
1. **Install pipenv (if not already installed):**
   ```bash
   pip install pipenv
   ```
2. **Install dependencies:**
   ```bash
   pipenv install --dev
   ```
3. **Activate the virtual environment:**
   ```bash
   pipenv shell
   ```
4. **Run the app:**
   ```bash
   streamlit run app/app.py
   ```
   The app will be available at [http://localhost:8501](http://localhost:8501)

### Docker (optional):
   ```bash
   docker build -t voice-separator:latest .
   docker run -p 8080:8080 voice-separator:latest
   ```
   The app will be available at [http://localhost:8080](http://localhost:8080)

## Buy Me a Coffee
[☕ Buy Me a Coffee](https://buymeacoffee.com/br3gan)

---

**Made with ❤️ using Streamlit and Demucs** 
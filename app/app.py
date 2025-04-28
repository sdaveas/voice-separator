import streamlit as st
import os
import tempfile
from pathlib import Path
import yt_dlp
import subprocess
import soundfile as sf
from main import separate_audio

# Set page config
st.set_page_config(
    page_title="Voice Separator",
    page_icon="🎵",
    layout="centered"
)

# Add custom CSS
st.markdown("""
<style>
.error-message {
    color: red;
    padding: 10px;
    border-radius: 5px;
    background-color: #ffebee;
}
.progress-message {
    color: #1E88E5;
    padding: 10px;
    border-radius: 5px;
    background-color: #E3F2FD;
}
</style>
""", unsafe_allow_html=True)

st.title("🎵 Voice Separator")
st.markdown(
    """
Separate vocals and melody from your audio files with AI.
Upload an audio file or provide a YouTube link to get separate tracks for vocals and melody.
    """
)

# Choose audio source
st.markdown("#### Choose your audio source:")
col_upload, col_yt = st.columns(2)
with col_upload:
    uploaded_file = st.file_uploader("Upload an audio file", type=['wav', 'mp3', 'm4a', 'flac'])
with col_yt:
    yt_url = st.text_input("Or paste a YouTube link:")

temp_audio_path = None
base_name = None
audio_duration = None

# Helper to get duration in seconds
def get_audio_duration(path):
    try:
        with sf.SoundFile(path) as f:
            return int(f.frames / f.samplerate)
    except Exception:
        return None

def download_youtube_audio(yt_url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'temp_audio.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(yt_url, download=True)
        temp_audio_path = ydl.prepare_filename(info).replace(info['ext'], 'wav')
        base_name = info.get('title', 'yt_audio')
    return temp_audio_path, base_name

def trim_audio_ffmpeg(input_path, output_path, start_sec, end_sec):
    duration = end_sec - start_sec
    command = [
        'ffmpeg', '-y', '-i', input_path,
        '-ss', str(start_sec),
        '-t', str(duration),
        '-acodec', 'copy',
        output_path
    ]
    subprocess.run(command, check=True)

# Get audio and duration
audio_ready = False
if 'yt_url_last' not in st.session_state:
    st.session_state['yt_url_last'] = None
if 'yt_audio_path' not in st.session_state:
    st.session_state['yt_audio_path'] = None
if 'yt_base_name' not in st.session_state:
    st.session_state['yt_base_name'] = None
if 'yt_audio_duration' not in st.session_state:
    st.session_state['yt_audio_duration'] = None

# Track last processed file/link
if 'last_uploaded_file' not in st.session_state:
    st.session_state['last_uploaded_file'] = None
if 'last_yt_url' not in st.session_state:
    st.session_state['last_yt_url'] = None

# Detect change in file or YouTube link
file_changed = uploaded_file is not None and uploaded_file != st.session_state['last_uploaded_file']
yt_changed = yt_url and yt_url != st.session_state['last_yt_url']

if file_changed or yt_changed:
    st.session_state['separation_done'] = False
    st.session_state['last_uploaded_file'] = uploaded_file
    st.session_state['last_yt_url'] = yt_url

if yt_url:
    if yt_url != st.session_state['yt_url_last']:
        with st.spinner("Downloading audio from YouTube..."):
            try:
                temp_audio_path, base_name = download_youtube_audio(yt_url)
                audio_duration = get_audio_duration(temp_audio_path)
                st.session_state['yt_audio_path'] = temp_audio_path
                st.session_state['yt_base_name'] = base_name
                st.session_state['yt_audio_duration'] = audio_duration
                st.session_state['yt_url_last'] = yt_url
            except Exception as e:
                st.error(f"Failed to download audio: {e}")
                temp_audio_path = None
                base_name = None
                audio_duration = None
    else:
        temp_audio_path = st.session_state['yt_audio_path']
        base_name = st.session_state['yt_base_name']
        audio_duration = st.session_state['yt_audio_duration']
    if temp_audio_path and os.path.exists(temp_audio_path):
        st.audio(temp_audio_path)
    else:
        st.error("Audio file could not be found or opened.")
    audio_ready = temp_audio_path is not None
elif uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        temp_audio_path = tmp_file.name
        base_name = os.path.splitext(uploaded_file.name)[0]
    audio_duration = get_audio_duration(temp_audio_path)
    st.audio(uploaded_file)
    st.write(f"File: {uploaded_file.name}")
    audio_ready = True

def stepper(label, key_prefix, min_value=0, max_value=59, default=0):
    # Initialize session state
    if f"{key_prefix}_value" not in st.session_state:
        st.session_state[f"{key_prefix}_value"] = default

    col_up, col_val, col_down = st.columns([1,1,1])
    with col_up:
        if st.button("▲", key=f"{key_prefix}_up"):
            if st.session_state[f"{key_prefix}_value"] < max_value:
                st.session_state[f"{key_prefix}_value"] += 1
    with col_val:
        st.write(f"{label}: {st.session_state[f'{key_prefix}_value']:02d}")
    with col_down:
        if st.button("▼", key=f"{key_prefix}_down"):
            if st.session_state[f"{key_prefix}_value"] > min_value:
                st.session_state[f"{key_prefix}_value"] -= 1
    return st.session_state[f"{key_prefix}_value"]

# Segment selection fields (MM:SS format)
if audio_ready and audio_duration:
    with st.expander("Select segment to process (optional):"):
        col_start, col_end = st.columns(2)
        with col_start:
            start_ts = st.text_input("Start (MM:SS or SS)", value="00:00", key="start_ts")
        with col_end:
            end_ts = st.text_input("End (MM:SS or SS)", value="", key="end_ts")

        def parse_ts(ts, default=0):
            try:
                if not ts:
                    return default
                parts = ts.split(":")
                if len(parts) == 2:
                    m, s = int(parts[0]), int(parts[1])
                    return m * 60 + s
                elif len(parts) == 1:
                    return int(parts[0])
            except Exception:
                return default
            return default

        segment_start = parse_ts(start_ts, 0)
        segment_end = parse_ts(end_ts, audio_duration)
        if segment_end == 0 or segment_end > audio_duration:
            segment_end = audio_duration
        if segment_start < 0:
            segment_start = 0
        if segment_end <= segment_start:
            segment_end = audio_duration

        # Format for display
        def fmt_ts(seconds):
            return f"{seconds//60:02d}:{seconds%60:02d}"

        st.write(f"Selected: {fmt_ts(segment_start)} - {fmt_ts(segment_end)}")

# Before the button
if 'separation_done' not in st.session_state:
    st.session_state['separation_done'] = False
if 'separating' not in st.session_state:
    st.session_state['separating'] = False

separate_disabled = st.session_state['separation_done'] or st.session_state['separating']
separate_clicked = st.button("Separate", key="separate_btn", disabled=separate_disabled)

if separate_clicked:
    separate_disabled = True

if separate_clicked:
    st.session_state['separating'] = True
    try:
        # Trim segment to a temp file if needed
        trimmed_path = temp_audio_path.replace('.wav', '_trimmed.wav')
        if segment_start > 0 or segment_end < audio_duration:
            trim_audio_ffmpeg(temp_audio_path, trimmed_path, segment_start, segment_end)
            process_path = trimmed_path
        else:
            process_path = temp_audio_path
        st.markdown("---")
        progress_bar = st.progress(0)
        status_text = st.empty()
        status_text.text("Loading audio...")
        progress_bar.progress(10)
        status_text.text("Separating vocals...")
        progress_bar.progress(40)
        status_text.text("Separating melody...")
        progress_bar.progress(70)
        output_vocals, output_melody = separate_audio(process_path, base_name)
        with open(output_vocals, 'rb') as f:
            st.session_state['vocals_bytes'] = f.read()
            os.remove(output_vocals)
        with open(output_melody, 'rb') as f:
            st.session_state['melody_bytes'] = f.read()
            os.remove(output_melody)
        with open(process_path, 'rb') as f:
            st.session_state['original_bytes'] = f.read()
            os.remove(process_path)
        os.remove(temp_audio_path)
        st.session_state['base_name'] = base_name
        st.session_state['separation_done'] = True
        st.session_state['separating'] = False
        status_text.text("Saving files...")
        progress_bar.progress(90)
        progress_bar.progress(100)
        status_text.text("Done!")
        st.success("Processing complete!")
    except Exception as e:
        st.session_state['separating'] = False
        st.error(f"An error occurred: {str(e)}")
        st.markdown(f'<div class="error-message">Error details: {str(e)}</div>', unsafe_allow_html=True)

# Always show processed results and download buttons if available
if st.session_state.get('separating', False) and not st.session_state.get('separation_done', False):
    st.info('Processing is ongoing. This may take a few moments...')

if all(k in st.session_state for k in ['vocals_bytes', 'melody_bytes', 'original_bytes', 'base_name']):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("Vocals")
        st.audio(st.session_state['vocals_bytes'], format="audio/wav")
    with col2:
        st.subheader("Melody")
        st.audio(st.session_state['melody_bytes'], format="audio/wav")
    with col3:
        st.subheader("Original")
        st.audio(st.session_state['original_bytes'], format="audio/wav")
    st.markdown("---")
    # st.subheader("Download Results")
    # col_voc, col_mel, col_orig = st.columns(3)
    # with col_voc:
    #     st.download_button(
    #         label="Download Vocals",
    #         data=st.session_state['vocals_bytes'],
    #         file_name=f"{st.session_state['base_name']}_vocals.wav",
    #         mime="audio/wav"
    #     )
    # with col_mel:
    #     st.download_button(
    #         label="Download Melody",
    #         data=st.session_state['melody_bytes'],
    #         file_name=f"{st.session_state['base_name']}_melody.wav",
    #         mime="audio/wav"
    #     )
    # with col_orig:
    #     st.download_button(
    #         label="Download Original",
    #         data=st.session_state['original_bytes'],
    #         file_name=f"{st.session_state['base_name']}_original.wav",
    #         mime="audio/wav"
    #     )

# Add a footer
st.markdown("---")
st.markdown("Made with ❤️ using from [br3gan](https://github.com/sdaveas/voice-separator)")
st.markdown(
    '<div style="margin: 1em 0;"><a href="https://buymeacoffee.com/br3gan" target="_blank" style="font-size:1.5em; font-weight:bold; color:#1976D2; text-decoration:none;">☕ Buy Me a Coffee</a></div>',
    unsafe_allow_html=True
) 
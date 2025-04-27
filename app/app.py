import streamlit as st
import os
import tempfile
from pathlib import Path
import sys
import torch
import torchaudio

# Import the separation function after setting the backend
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

def main():
    st.title("🎵 Voice Separator")
    st.markdown(
        """
Separate vocals and melody from your audio files with AI.
Upload an audio file and get separate tracks for vocals and melody.
        """
    )

    # File uploader
    uploaded_file = st.file_uploader("Choose an audio file", type=['wav', 'mp3', 'm4a', 'flac'])

    if uploaded_file is not None:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name

        # Show file details
        st.audio(uploaded_file)
        st.write(f"File: {uploaded_file.name}")
        
        # Add a separator
        st.markdown("---")
        
        # Process button
        # if st.button("Separate Tracks"):
        try:
            # Get the base name without extension
            base_name = os.path.splitext(uploaded_file.name)[0]
            
            # Create a progress container
            progress_container = st.empty()
            progress_container.markdown('<div class="progress-message">Processing audio... This may take a few minutes.</div>', unsafe_allow_html=True)
            
            # Process the audio
            output_vocals, output_melody = separate_audio(tmp_path, base_name)
            
            # Clear progress message
            progress_container.empty()
            
            # Display results
            st.success("Processing complete!")
            
            # Create two columns for the audio players
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Vocals")
                st.audio(output_vocals)
                st.download_button(
                    label="Download Vocals",
                    data=open(output_vocals, 'rb').read(),
                    file_name=f"{base_name}_vocals.wav",
                    mime="audio/wav"
                )
            
            with col2:
                st.subheader("Melody")
                st.audio(output_melody)
                st.download_button(
                    label="Download Melody",
                    data=open(output_melody, 'rb').read(),
                    file_name=f"{base_name}_melody.wav",
                    mime="audio/wav"
                )
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.markdown(f'<div class="error-message">Error details: {str(e)}</div>', unsafe_allow_html=True)
        finally:
            # Clean up temporary file
            try:
                os.unlink(tmp_path)
            except:
                pass

    # Add some helpful information
    st.markdown(
        """
### Tips:
- For best results, use high-quality audio files
- Processing time depends on the length of the audio
- Supported formats: WAV, MP3, M4A, FLAC
        """
    )

    # Add a footer
    st.markdown("---")
    st.markdown("Made with ❤️ using Streamlit and Demucs")
    st.markdown(
        '<div style="margin: 1em 0;"><a href="https://buymeacoffee.com/br3gan" target="_blank" style="font-size:1.5em; font-weight:bold; color:#FFDD00; text-decoration:none;">☕ Buy Me a Coffee</a></div>',
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main() 
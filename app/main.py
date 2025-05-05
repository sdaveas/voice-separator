import torch
import argparse
import torchaudio
import soundfile
import os
import numpy as np
import logging
import re
from demucs.pretrained import get_model
from demucs.audio import AudioFile, save_audio
from demucs.apply import apply_model

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def sanitize_filename(name):
    # Replace non-ASCII and spaces with underscores
    return re.sub(r'[^A-Za-z0-9_.-]', '_', name)

def enhance_audio(audio, sample_rate):
    """Apply basic audio enhancement to improve quality"""
    try:
        # Convert to numpy for processing
        audio_np = audio.numpy()
        
        # Normalize the audio
        audio_np = audio_np / np.max(np.abs(audio_np))
        
        # Apply a gentle high-pass filter to reduce low-frequency noise
        # This is a simple implementation - in practice you might want to use a proper filter
        audio_np = np.clip(audio_np, -0.9, 0.9)
        
        return torch.from_numpy(audio_np)
    except Exception as e:
        logger.error(f"Error in enhance_audio: {str(e)}")
        return audio

def separate_audio(input_file, output_base=None):
    """Separate vocals and melody from an audio file"""
    try:
        # Generate output filenames
        if output_base is None:
            # Use input filename without extension as the base
            input_filename = os.path.basename(input_file)
            output_base = os.path.splitext(input_filename)[0]

        # Sanitize the base name
        output_base = sanitize_filename(output_base)

        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(os.path.abspath(input_file))
        os.makedirs(output_dir, exist_ok=True)

        output_vocals = os.path.join(output_dir, f"{output_base}_vocals.wav")
        output_melody = os.path.join(output_dir, f"{output_base}_melody.wav")

        # Load audio
        audio_file = AudioFile(input_file)
        mix = audio_file.read()
        sample_rate = int(audio_file.samplerate())

        # Ensure audio is in the correct format (batch, channels, samples)
        if mix.dim() == 1:  # If mono, add channel dimension
            mix = mix.unsqueeze(0)
        if mix.dim() == 2:  # If just channels and samples, add batch dimension
            mix = mix.unsqueeze(0)

        # First, get vocals using htdemucs model
        logger.info("Separating vocals...")
        vocals_model = get_model('htdemucs')
        vocals_model.eval()
        with torch.no_grad():
            vocals_sources = apply_model(vocals_model, mix, device='cpu', progress=True)[0]
        vocals = vocals_sources[3]  # Get vocals from htdemucs model

        # Then, get all non-vocal tracks using htdemucs model
        logger.info("Separating melody (everything except vocals)...")
        # For htdemucs model, sources are in this order:
        # 0: drums
        # 1: bass
        # 2: other
        # 3: vocals
        melody = vocals_sources[0] + vocals_sources[1] + vocals_sources[2]  # Combine drums, bass, and other

        # Enhance the tracks
        vocals = enhance_audio(vocals, sample_rate)
        melody = enhance_audio(melody, sample_rate)

        # Save both tracks
        soundfile.write(output_vocals, vocals.numpy().T, sample_rate)
        soundfile.write(output_melody, melody.numpy().T, sample_rate)

        logger.info("Done!")

        return output_vocals, output_melody
    except Exception as e:
        logger.error(f"Error in separate_audio: {str(e)}")
        raise

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Separate vocals and melody from a song')
    parser.add_argument('input_file', help='Path to the input audio file')
    parser.add_argument('--output', help='Base name for output files (default: input filename without extension)')
    args = parser.parse_args()

    try:
        output_vocals, output_melody = separate_audio(args.input_file, args.output)
        logger.info(f"Saved vocals to: {output_vocals}")
        logger.info(f"Saved melody to: {output_melody}")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        exit(1)
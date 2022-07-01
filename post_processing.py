"""
post_processing.py

cleans up audio files and trims length
"""
from pydub.silence import split_on_silence

def audio_post_processing(sound):
    """cleans up the audio file

    Args:
        sound (AudioSegment): an audio clip of a spoken word
    """

    sound = split_on_silence(
            sound,
            silence_thresh=-50,
            keep_silence=False,
            min_silence_len=300
        )[0] 
    
    sound.apply_gain(-20 - sound.dBFS)

    return sound
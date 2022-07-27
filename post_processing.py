"""
post_processing.py

cleans up audio files, trims length and saves to disk
"""
from pydub.silence import split_on_silence

def audio_post_processing(sound):
    """cleans up the audio file

    Args:
        sound (AudioSegment): an audio clip of a spoken word
    """

    sound = split_on_silence(
            sound,
            silence_thresh=-40,
            keep_silence=False,
            min_silence_len=50
        )

    return sound


def audio_to_file_segment(sound, start=0, end=None, filename=None):
    """splits an audio clip into a segment of audio

    Args:
        sound (AudioSegment): an audio clip of a spoken word
        start (int): the start time of the segment
        end (int): the end time of the segment
        filename (str): the name of the file to save the segment to
    """

    if end is None:
        end = len(sound)

    if filename is None:
        filename = "./temp.wav"

    sound[start * 1000:end * 1000].export(filename, format=filename.split(".")[-1])

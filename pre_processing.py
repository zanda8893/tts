from pydub import AudioSegment


def file_to_audio_segment(file_path):
    return AudioSegment.from_file(file_path)

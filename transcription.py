#!./venv/bin/python3
# https://stackoverflow.com/questions/64153590/audio-signal-split-at-word-level-boundary

import sys
import json
import math

# tested with VOSK 0.3.15
import vosk
import librosa
import numpy


def __extract_words(res):
    jres = json.loads(res)
    if not 'result' in jres:
        return []
    words = jres['result']
    return words


def __transcribe_words(recognizer, bytes):
    results = []
    chunk_size = 4000

    for chunk_no in range(math.ceil(len(bytes) / chunk_size)):
        start = chunk_no * chunk_size
        end = min(len(bytes), (chunk_no + 1) * chunk_size)
        data = bytes[start:end]

        if recognizer.AcceptWaveform(data):
            words = __extract_words(recognizer.Result())
            results += words
    results += __extract_words(recognizer.FinalResult())

    return results


def transcribe_wav(audio_path):
    vosk.SetLogLevel(-1)

    audio, sr = librosa.load(audio_path, sr=48000)

    return __transcribe_words(vosk.KaldiRecognizer(vosk.Model("vosk-model-small-en-us-0.15"), 48000),
                              numpy.int16(audio * 32768).tobytes())  # convert to 16bit signed PCM, as expected by VOSK


if __name__ == '__main__':
    transcribe_wav(sys.argv[1])

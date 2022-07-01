#!/usr/bin/python3
import logging
import asyncio

from pydub.playback import play 
from pydub.silence import split_on_silence

from online import get_mp3_from_wordlist

logging.basicConfig(level=logging.INFO)

def main():
    # Read in sentence from stdin
    sentence = input("Enter sentence: ")
    # Split sentence into words
    words = sentence.split()

    ##Method 1
    # request online
    list_of_sounds = asyncio.run(get_mp3_from_wordlist(words))

    # Post process mp3s
    for sound in list_of_sounds:
        # extract word
        sound = split_on_silence(
            sound,
            silence_thresh=-50,
            keep_silence=False,
            min_silence_len=300
        )[0] # +  AudioSegment.silent(duration=400)

        # balance audio
        sound.apply_gain(-20 - sound.dBFS)
    
    ##Method 2
    # database



if __name__ == "__main__":
    main()

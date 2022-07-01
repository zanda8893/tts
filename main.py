#!/usr/bin/python3
import logging

from pydub.playback import play 

import online
import database

logging.basicConfig(level=logging.INFO)

def main():
    # Read in sentence from stdin
    sentence = input("Enter sentence: ")
    # Split sentence into words
    words = sentence.split()

    ##Method 1
    # request online
    list_of_sounds = online.get_mp3s_from_wordlist(words)
    # play sound
    for sound in list_of_sounds:
        play(sound)
    
    ##Method 2
    # database
    list_of_sounds = database.get_mp3s_from_wordlist(words)


if __name__ == "__main__":
    main()

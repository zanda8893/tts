#!/usr/bin/python3
import logging

from pydub.playback import play 

from online import get_mp3_from_wordlist

logging.basicConfig(level=logging.INFO)

def main():
    # Read in sentence from stdin
    sentence = input("Enter sentence: ")
    # Split sentence into words
    words = sentence.split()

    ##Method 1
    # request online
    list_of_sounds = get_mp3_from_wordlist(words)
    
    ##Method 2
    # database



if __name__ == "__main__":
    main()

#!/usr/bin/python3
import logging

import asyncio
import aiohttp
from bs4 import BeautifulSoup

import re
import base64
from io import BytesIO

from pydub import AudioSegment
from pydub.playback import play 
from pydub.silence import split_on_silence


logging.basicConfig(level=logging.INFO)
HDR = {
    'User-Agent': '''Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) \
    Chrome/23.0.1271.64 Safari/537.11''',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'
}

async def find_mp3(page): #Find the mp3 link from forvo website = Class download word
    """
    Finds the mp3 from the webpage from word page forvo
    """
    index = BeautifulSoup(page, 'html.parser')
    # find span with class play  icon-size-l
    span = index.find('span', {"id" : re.compile('play_*')})

    print(span)
    # get onclick method
    onclick = span.get('onclick')
    # remove play( and ) from onclick method
    onclick = onclick[5:-1]

    # get second element
    play_id = onclick.split(",")[1]
    # get id of audio track
    play_id = base64.b64decode(play_id).decode('utf-8')

    return play_id


async def request_mp3_from_forvo(session, word):
    async with session.get("https://forvo.com/search/" + word +"/en/") as response:
        forvo_data = await response.text()
        # parse webpage
        play_id =  await find_mp3(forvo_data)
    
    # Download mp3 from forvo
    async with session.get("https://forvo.com/mp3/" + play_id) as response:
        return AudioSegment.from_mp3(BytesIO(await response.read()))


async def get_mp3(words):
    """
    Gets mp3 file for word
    """
    # Download from webpage
    print("Downloading mp3 files")

    async with aiohttp.ClientSession(headers=HDR) as session:
        tasks = []
        for word in words:
            tasks.append(asyncio.ensure_future(request_mp3_from_forvo(session, word)))
        forvo_data = await asyncio.gather(*tasks)
    
    return forvo_data


def main():
    # Read in sentence from stdin
    sentence = input("Enter sentence: ")
    # Split sentence into words
    words = sentence.split()
    # Get mp3 for each word
    list_of_sounds = asyncio.run(get_mp3(words))

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


if __name__ == "__main__":
    main()

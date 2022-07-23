"""
online.py

goes though each word on a word list and downloads the mp3 from forvo
"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup

import re
import base64
from io import BytesIO

from pydub import AudioSegment

from post_processing import audio_post_processing

HDR = {
    'User-Agent': '''Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) \
    Chrome/23.0.1271.64 Safari/537.11''',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'
}

def get_mp3_from_word(word):
    """downloads the mp3 for a single word

    Args:
        word (str): a single word
    """
    sound = asyncio.run(get_mp3(word))
    return sound

async def get_mp3(word):
    """
    Downloads the mp3 file of a word
    """
    # Download from webpage
    print("Downloading mp3 file")

    async with aiohttp.ClientSession(headers=HDR) as session:
        await __request_mp3_from_forvo(session, word)
    return word

def get_mp3s_from_wordlist(words):
    """downloads mp3 from wordlist

    Args:
        words (list): a list of words in a sentence
    """
    list_of_words = asyncio.run(get_mp3s(words))

    for word in list_of_words:
        word = audio_post_processing(word)

    return list_of_words

async def get_mp3s(words):
    """
    Downloads each mp3 file for a wordlist using asyncio
    """
    # Download from webpage
    print("Downloading mp3 files")

    async with aiohttp.ClientSession(headers=HDR) as session:
        tasks = []
        for word in words:
            tasks.append(asyncio.ensure_future(__request_mp3_from_forvo(session, word)))
        forvo_data = await asyncio.gather(*tasks)

    return forvo_data

async def __parse_forvo(page):
    """
    parses html for the mp3 id
    """
    index = BeautifulSoup(page, 'html.parser')
    # find span with class play  icon-size-l
    if index.find('article', {"class" : re.compile('search_words empty')}):
        print("Failed to find word on Forvo")
        return 1

    div = index.find('div', {"id" : re.compile('play_\d+')})

    # print(span)
    # get onclick method
    onclick = div.get('onclick')
    # remove play( and ) from onclick method
    onclick = onclick[5:-1]

    # get second element
    play_id = onclick.split(",")[1]
    # get id of audio track
    play_id = base64.b64decode(play_id).decode('utf-8')

    return play_id

async def __request_mp3_from_forvo(session, word):
    """
    requests forvo for the mp3 id and then downloads it
    """
    async with session.get("https://forvo.com/search/" + word +"/en/") as response:
        forvo_data = await response.text()
        # parse webpage
        play_id =  await __parse_forvo(forvo_data)

    # Download mp3 from forvo
    async with session.get("https://forvo.com/mp3/" + play_id) as response:
        return AudioSegment.from_mp3(BytesIO(await response.read()))

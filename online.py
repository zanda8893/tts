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
    parses html for the mp3 id
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
    """
    requests forvo for the mp3 id and then downloads it
    """
    async with session.get("https://forvo.com/search/" + word +"/en/") as response:
        forvo_data = await response.text()
        # parse webpage
        play_id =  await find_mp3(forvo_data)
    
    # Download mp3 from forvo
    async with session.get("https://forvo.com/mp3/" + play_id) as response:
        return AudioSegment.from_mp3(BytesIO(await response.read()))


async def get_mp3_from_wordlist(words):
    """
    Downloads each mp3 file for a wordlist
    """
    # Download from webpage
    print("Downloading mp3 files")

    async with aiohttp.ClientSession(headers=HDR) as session:
        tasks = []
        for word in words:
            tasks.append(asyncio.ensure_future(request_mp3_from_forvo(session, word)))
        forvo_data = await asyncio.gather(*tasks)
    
    return forvo_data
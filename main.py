#!/usr/bin/python3
import time
import os
import base64
import re
import logging
import asyncio
from io import BytesIO

import aiohttp
from bs4 import BeautifulSoup
from tqdm import tqdm
from pydub import AudioSegment
from pydub.playback import play
from pydub.silence import split_on_silence

import numpy as np
import matplotlib.pyplot as plt

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



#     async def remove_silence(self, silence_threshold=-40, chunk_size=10): #Seperate function or class
#         """
#         sound is a pydub.AudioSegment
#         silence_threshold in dB
#         chunk_size in ms
#         iterate over chunks until you find the first one with sound
#         """
#         trim_ms = 0 # ms
#         trim_ms_reversed = 0
#         sound_reversed = self.sound.reverse()
#         length = len(self.sound)
#         assert chunk_size > 0 # to avoid infinite loop
#         if self.sound:
#             while self.sound[trim_ms:trim_ms+chunk_size].dBFS < silence_threshold and trim_ms < length:
#                 trim_ms += chunk_size
#             while sound_reversed[trim_ms_reversed:trim_ms_reversed+chunk_size].dBFS < silence_threshold and trim_ms_reversed < length:
#                 trim_ms_reversed += chunk_size
#             self.sound = self.sound[trim_ms:length-trim_ms_reversed+400]
#             logging.debug(" [+] Trimmed: %s Total: %s", trim_ms+trim_ms_reversed, length)
#         return

#     async def level(self): #Seperate function or class
#         self.sound = self.sound.apply_gain( -20 - self.sound.dBFS)
#         return

#     async def extract_word(self, num): #Seperate function or class
#         self.sound = split_on_silence(
#             self.sound,
#             silence_thresh=-50,
#             keep_silence=False,
#             min_silence_len=300
#         )[num] +  AudioSegment.silent(duration=400)

#     async def write_file(self): #Class download word
#         #file = open(self.word + ".mp3", "wb")
#         self.sound.export("./cache/" + self.word + ".mp3", format="mp3")
#         #file.close()

# def formsentence(words):
#     sentence = AudioSegment.empty()
#     for word in words:
#         print(word.word)
#         play(word.sound)
#         sentence += word.sound
#     sentence.export("./sentence.mp3", format="mp3")
#     return sentence

# def joinMp3(files):
#     """
#     Joins multiple mp3 files
#     """
#     logging.info("[*] Joining files")
#     sentencefiles = AudioSegment.empty()
#     for file in tqdm(files):
#         word = AudioSegment.from_mp3("./" + file)
#         sentencefiles += word
#     sentencefiles.export("./sentence.mp3", format="mp3")
#     logging.info("[*] Joined files!")
#     return sentencefiles

# # async def get_mp3(word):
# #     if not word.downloaded:
# #         print(word.downloaded)
# #         await word.get_web_page()
# #         logging.info("[*] Found page for %s", word.word)
# #         await word.find_mp3()
# #         logging.info("  [+] Found mp3")
# #         await word.download_mp3()
# #         logging.info("  [+] Downloaded")
# #     await word.extract_word(0)
# #     await word.level()
# #     logging.info("  [+] Processed")
# #     await word.write_file()

# def graph_audio(word):
#     samplerate, data = read(word.word+".mp3")
#     duration = len(data)/samplerate
#     timerange = np.arange(0, duration, 1/samplerate)
#     # Plotting the Graph using Matplotlib
#     plt.plot(timerange, data)
#     plt.xlabel('Time [s]')
#     plt.ylabel('Amplitude')
#     plt.title(word.word)
#     play(word.sound)
#     plt.show()

# def read(f, normalized=False):
#     """MP3 to numpy array"""
#     a = AudioSegment.from_mp3(f)
#     y = np.array(a.get_array_of_samples())
#     if a.channels == 2:
#         y = y.reshape((-1, 2))
#     if normalized:
#         return a.frame_rate, np.float32(y) / 2**15
#     else:
#         return a.frame_rate, y






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
    mp3s = asyncio.run(get_mp3(words))

    for mp3 in mp3s:
        play(mp3)
    # SENTENCE = input("Enter a sentence: ")
    # start_time = time.time()
    # getmp3 = []
    # for SENword in SENTENCE.split(" "):
    #     try:
    #         wordClass = words[SENword]
    #         getmp3.append(get_mp3(wordClass))
    #     except KeyError:
    #         wordClass = Word(SENword.lower())
    #         words[SENword] = wordClass
    #         getmp3.append(get_mp3(wordClass))
    # await asyncio.gather(*getmp3)
    # #graph_audio(wordClass)
    # SENTENCE = formsentence(words.values())
    # return start_time

if __name__ == "__main__":
    main()

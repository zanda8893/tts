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

class Word:
    """
    A class to convert word to speach aka tts
    """
    def __init__(self, word):
        self.word = word
        self.page = None
        self.path = None
        self.sound = None
        self.downloaded = False

    async def get_web_page(self): #Class to get the web page that shoudl contain a link to download the word = Class download word
        """
        Downloads the website page from forvo
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    "https://forvo.com/search/" + self.word +"/en/",
                    headers=HDR
                ) as resp:
                self.page = await resp.read()
        return

    async def find_mp3(self): #Find the mp3 link from forvo website = Class download word
        """
        Finds the mp3 from the webpage from word page forvo
        """
        index = BeautifulSoup(self.page, 'html.parser')
        if index.findAll("span", {"id" : re.compile('play_*')}):
            idplay_ = str(
                index.findAll(
                    "span", {"id" : re.compile('play_*')}
                )[0] #html element (span) with ID = "play_" #Returns single item in list
            )#Convert BS4 attribute to string
            self.path = base64.b64decode(
                str(
                    idplay_.split(",")[1]
                )
            ).decode("utf-8")
            return
        logging.info("[-] Failed to find mp3 for %s", self.word)
        await self.gen_word()
        return

    async def download_mp3(self): #Download the mp3 = Class download word
        """
        Download the mp3 from forvo - Could be modified to download from any website
        """
        if self.path is None:
            return
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    "https://forvo.com/mp3/" + self.path,
                    headers=HDR
                ) as resp:
                self.sound = AudioSegment.from_mp3(BytesIO(await resp.read()))
                #play(self.sound)
                self.downloaded = True
        return

    async def gen_word(self): #Generate the word if it cannot be found in our library = Class download word
        """
        Generates the word using mimic if it cannot be found online
        """
        os.system(
            "/home/zanda/mycroft-core/mimic/bin/mimic -t '" + self.word +"' " + self.word + ".wav"
        )
        self.sound = AudioSegment.from_wav("./" + self.word + ".wav")
        return

    async def remove_silence(self, silence_threshold=-40, chunk_size=10): #Seperate function or class
        """
        sound is a pydub.AudioSegment
        silence_threshold in dB
        chunk_size in ms
        iterate over chunks until you find the first one with sound
        """
        trim_ms = 0 # ms
        trim_ms_reversed = 0
        sound_reversed = self.sound.reverse()
        length = len(self.sound)
        assert chunk_size > 0 # to avoid infinite loop
        if self.sound:
            while self.sound[trim_ms:trim_ms+chunk_size].dBFS < silence_threshold and trim_ms < length:
                trim_ms += chunk_size
            while sound_reversed[trim_ms_reversed:trim_ms_reversed+chunk_size].dBFS < silence_threshold and trim_ms_reversed < length:
                trim_ms_reversed += chunk_size
            self.sound = self.sound[trim_ms:length-trim_ms_reversed+400]
            logging.debug(" [+] Trimmed: %s Total: %s", trim_ms+trim_ms_reversed, length)
        return

    async def level(self): #Seperate function or class
        self.sound = self.sound.apply_gain( -20 - self.sound.dBFS)
        return

    async def extract_word(self, num): #Seperate function or class
        self.sound = split_on_silence(
            self.sound,
            silence_thresh=-50,
            keep_silence=False,
            min_silence_len=300
        )[num] +  AudioSegment.silent(duration=400)

    async def write_file(self): #Class download word
        #file = open(self.word + ".mp3", "wb")
        self.sound.export("./cache/" + self.word + ".mp3", format="mp3")
        #file.close()

def formsentence(words):
    sentence = AudioSegment.empty()
    for word in words:
        print(word.word)
        play(word.sound)
        sentence += word.sound
    sentence.export("./sentence.mp3", format="mp3")
    return sentence

def joinMp3(files):
    """
    Joins multiple mp3 files
    """
    logging.info("[*] Joining files")
    sentencefiles = AudioSegment.empty()
    for file in tqdm(files):
        word = AudioSegment.from_mp3("./" + file)
        sentencefiles += word
    sentencefiles.export("./sentence.mp3", format="mp3")
    logging.info("[*] Joined files!")
    return sentencefiles

async def get_mp3(word):
    if not word.downloaded:
        print(word.downloaded)
        await word.get_web_page()
        logging.info("[*] Found page for %s", word.word)
        await word.find_mp3()
        logging.info("  [+] Found mp3")
        await word.download_mp3()
        logging.info("  [+] Downloaded")
    await word.extract_word(0)
    await word.level()
    logging.info("  [+] Processed")
    await word.write_file()

def graph_audio(word):
    samplerate, data = read(word.word+".mp3")
    duration = len(data)/samplerate
    timerange = np.arange(0, duration, 1/samplerate)
    # Plotting the Graph using Matplotlib
    plt.plot(timerange, data)
    plt.xlabel('Time [s]')
    plt.ylabel('Amplitude')
    plt.title(word.word)
    play(word.sound)
    plt.show()

def read(f, normalized=False):
    """MP3 to numpy array"""
    a = AudioSegment.from_mp3(f)
    y = np.array(a.get_array_of_samples())
    if a.channels == 2:
        y = y.reshape((-1, 2))
    if normalized:
        return a.frame_rate, np.float32(y) / 2**15
    else:
        return a.frame_rate, y

async def main(words):
    SENTENCE = input("Enter a sentence: ")
    start_time = time.time()
    getmp3 = []
    for SENword in SENTENCE.split(" "):
        try:
            wordClass = words[SENword]
            getmp3.append(get_mp3(wordClass))
        except KeyError:
            wordClass = Word(SENword.lower())
            words[SENword] = wordClass
            getmp3.append(get_mp3(wordClass))
    await asyncio.gather(*getmp3)
    #graph_audio(wordClass)
    SENTENCE = formsentence(words.values())
    return start_time

if __name__ == "__main__":
    while True:
        words = {}
        start_time = asyncio.run(main(words))
        print("--- %s thread time seconds ---" % round(time.thread_time(), 2))
        print("--- %s thread time seconds ---" % round(time.thread_time(), 2))
        print("--- %s seconds---" % round(time.time() - start_time, 2))
        #play(SENTENCE)

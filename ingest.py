#!./venv/bin/python3
import csv
from os import listdir
from pre_processing import file_to_audio_segment
from post_processing import audio_post_processing, audio_to_file_segment
from transcription import transcribe_wav
from tqdm import tqdm
from pydub.playback import play


def openslr83(f):  # https://openslr.org/83/
    for file in f:
        with open("./data_imports/" + file + "/line_index.csv", 'r', newline='') as csvfileraw:
            csvfile = csv.reader(csvfileraw, delimiter=',', quotechar='|')
            for row in tqdm(csvfile):
                wav_path = "./data_imports/" + file + "/" + row[1][1:] + ".wav"  # path to wav file being ingested
                sound = file_to_audio_segment(wav_path)

                transcription = row[2].split(" ")  # transcription of wav file from dataset

                words = transcribe_wav(wav_path)  # transcription of wav file from VOSK

                if len(words) != len(transcription):  # if dataset transcription and VOSK are not the same length
                    continue

                for count, word in enumerate(words):
                    if float(word["conf"]) == 1.0 and word["word"] == transcription[count]:
                        audio_to_file_segment(sound, word["start"], word["end"], "./data/" + word["word"] + ".wav")


if __name__ == "__main__":
    files = listdir("data_imports")

    print("Select which files to import from /data_imports")
    for num, filename in enumerate(files):
        print("    ", filename, " ", num)

    sel = input("Select which number to import or ALL ")
    if sel == "ALL":
        openslr83(files)
    else:
        print([files[int(sel)]])
        openslr83([files[int(sel)]])

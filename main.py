import subprocess
import os

def recursive():

    folders = get_folders()
    if folders != []:
        for folder in folders:
            os.chdir(folder)
            recursive()
            os.chdir('..')
    else:
        place = os.getcwd()
        files = next(os.walk(place))[2]
        for file in files:
            if file.endswith('.flac') and file.replace('.flac', '.opus') not in files:
                subprocess.run(['ffmpeg', "-i", place+"\\"+file, "-map", "0:0", "-c:a", "copy", "-acodec", "libopus", file.replace('.flac', '.opus')])

def get_folders():
    return next(os.walk('.'))[1]

if __name__ == "__main__":
    initial_dir = os.getcwd()
    recursive()







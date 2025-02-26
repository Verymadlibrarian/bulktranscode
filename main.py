import subprocess
import os

def recursive():
    actual_dir = os.getcwd()
    folders = get_folders()

    final_dir = destination+actual_dir.replace(initial_dir, '') #Gets the destination + the actual directory structure
    os.mkdir(final_dir)

    if folders:
        
        for folder in folders: #For every folder, get into it and recursively call the function
            os.chdir(folder)
            recursive()
            os.chdir('..')
    else: #If there are no folders, get the files and convert them
        files = get_files()
        
        for file in files:
            if file.endswith(init_extension) and file.replace(init_extension, final_extension) not in files:

                subprocess.run(['ffmpeg', "-i", file, "-map", "0:0","-acodec", "libopus", final_dir+"\\"+file.replace(init_extension, final_extension)])


def get_folders():
    return next(os.walk('.'))[1]

def get_files():
    return next(os.walk('.'))[2]

if __name__ == "__main__":
    initial_dir = (input("Source folder :"))
    initial_dir = fr"{initial_dir}"
    destination = (input("Source folder :"))
    destination = fr"{destination}"
    os.chdir(initial_dir)
    init_extension = '.flac'
    final_extension = '.opus'
    recursive()

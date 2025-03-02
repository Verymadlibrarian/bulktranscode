import os
import subprocess
import shutil

# Mapping of codecs to ffmpeg codec names and file extensions.
CODEC_NAME = {
    "aac": "aac",
    "flac": "flac",
    "opus": "libopus",
    "mp3": "libmp3lame",
    "vorbis": "libvorbis",
}

FILE_EXTENSION = {
    "aac": ".aac",
    "flac": ".flac",
    "opus": ".opus",
    "mp3": ".mp3",
    "vorbis": ".ogg",
}

def gather_files(source_folder, destination_folder, source_codec, target_codec, copy_other_files):
    """
    Walk through the source folder and prepare a list of files to process.
    Returns a list of tuples: (input_file, output_file, mode) where mode is "transcode" or "copy".
    """
    files_to_process = []
    ext1 = FILE_EXTENSION[source_codec]
    ext2 = FILE_EXTENSION[target_codec]
    for root, _, files in os.walk(source_folder):
        relative_path = os.path.relpath(root, source_folder)
        out_dir = os.path.join(destination_folder, relative_path)
        os.makedirs(out_dir, exist_ok=True)
        for file in files:
            input_path = os.path.join(root, file)
            if file.endswith(ext1):
                output_file = file.replace(ext1, ext2)
                output_path = os.path.join(out_dir, output_file)
                if not os.path.exists(output_path):
                    files_to_process.append((input_path, output_path, "transcode"))
            elif copy_other_files:
                output_path = os.path.join(out_dir, file)
                if not os.path.exists(output_path):
                    files_to_process.append((input_path, output_path, "copy"))
    return files_to_process

def process_file(input_file, output_file, mode, target_codec):
    """
    Process a single file by transcoding it or copying it.
    """
    if mode == "transcode":
        subprocess.run([
            'ffmpeg', '-i', input_file,
            '-acodec', CODEC_NAME[target_codec],
            output_file
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    elif mode == "copy":
        shutil.copy2(input_file, output_file)

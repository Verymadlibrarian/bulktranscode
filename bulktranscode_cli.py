import os
import argparse
from bulktranscode_core import gather_files, process_file, CODEC_NAME, FILE_EXTENSION

def run_cli(args):
    print("Running in command-line mode with the following parameters:")
    print("Source codec:", args.source_codec)
    print("Target codec:", args.target_codec)
    print("source folder:", args.source_folder)
    print("Destination folder:", args.destination_folder)
    print("Copy other files:", args.copy_others)

    files_to_process = gather_files(args.source_folder, args.destination_folder,
                                    args.source_codec, args.target_codec, args.copy_others)
    total = len(files_to_process)
    for idx, (input_file, output_file, mode) in enumerate(files_to_process):
        progress = int(((idx + 1) / total) * 100) if total > 0 else 100
        if mode == "transcode":
            print(f"Transcoding: {os.path.basename(input_file)} -> {os.path.basename(output_file)} ({progress}%)")
        else:
            print(f"Copying: {os.path.basename(input_file)} -> {os.path.basename(output_file)} ({progress}%)")
        process_file(input_file, output_file, mode, args.target_codec)
    print("Transcoding completed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BulkTranscode - Transcode audio files recursively")
    parser.add_argument("--source-codec", choices=["aac", "flac", "opus", "mp3", "vorbis"],
                        required=True, help="Source codec")
    parser.add_argument("--target-codec", choices=["aac", "flac", "opus", "mp3", "vorbis"],
                        required=True, help="Target codec")
    parser.add_argument("--source-folder", required=True, help="Folder containing source audio files")
    parser.add_argument("--destination-folder", required=True, help="Folder to output transcoded audio files")
    parser.add_argument("--copy-others", action="store_true",
                        help="Copy files that do not match the source codec extension")
    args = parser.parse_args()
    run_cli(args)

import argparse

def main():
    parser = argparse.ArgumentParser(description="BulkTranscode - Transcode audio files recursively - v0.6")
    parser.add_argument("--source-codec", choices=["aac", "flac", "opus", "mp3", "vorbis"],
                        help="Source codec")
    parser.add_argument("--target-codec", choices=["aac", "flac", "opus", "mp3", "vorbis"],
                        help="Target codec")
    parser.add_argument("--source-folder",
                        help="Folder containing source audio files")
    parser.add_argument("--destination-folder",
                        help="Folder to output transcoded audio files")
    parser.add_argument("--copy-others", action="store_true",
                        help="Copy files that do not match the source codec extension")
    args = parser.parse_args()

    # Run CLI mode if all required parameters are provided.
    if args.source_codec and args.target_codec and args.source_folder and args.destination_folder:
        from bulktranscode_cli import run_cli
        run_cli(args)
    else:
        # Otherwise, run the GUI. PyQt6 is imported only in the UI.
        from bulktranscode_ui import run_gui
        run_gui()

if __name__ == "__main__":
    main()

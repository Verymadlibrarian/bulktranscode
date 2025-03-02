# BulkTranscode

Transcode all your music library from one format to another while keeping the same folder structure.

## Screenshots

![screenshot](https://github.com/user-attachments/assets/e7876125-ade7-4f5d-904c-a1c13a69b461)

## Requirements

- Have `ffmpeg` in your PATH.  
  - On Linux: Install the `ffmpeg` package via your package manager.  
  - On Windows: Download and install the essential build from [FFmpeg's official site](https://www.ffmpeg.org/download.html). To have it in your PATH, either set the env. variables or copy `ffmpeg.exe` to `C:\Windows\System32`.

- Install PyQt6 with `pip install pyqt6`.

## Usage

### Formats supported ✅

- AAC
- FLAC
- MP3
- VORBIS
- WAV

### GUI mode

- Just launch the main file without any arguments and a Qt window will appear.
- Select all your settings in preferences and hit Start.

### Command line mode

- Launch the program with arguments like this : `python bulktranscode.py --source-codec flac --target-codec opus --source-folder "/path/to/source" --destination-folder "/path/to/destination" --copy-others`

## Fonctionalities

- ✅ Option to copy files that are not the main targets
- ❌ Option to set bitrate
- ❌ Handle if there are errors from ffmpeg
- Add more formats
- Fork this for videos also ?

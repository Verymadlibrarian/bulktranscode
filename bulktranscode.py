import sys
import os
import subprocess
import argparse
import shutil
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QDialog, QWidget, QLabel,
    QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QComboBox,
    QFileDialog, QStatusBar, QMessageBox, QTableWidget, QTableWidgetItem, 
    QHeaderView, QCheckBox
)
from PyQt6.QtGui import QAction, QColor
from PyQt6.QtCore import Qt, QThread, pyqtSignal

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


class TranscodeWorker(QThread):
    """
    Worker thread that recursively transcodes (or copies) files.
    Emits a signal with the input file, output file, mode ("transcode" or "copy"),
    and the overall progress percentage.
    """
    progress_signal = pyqtSignal(str, str, str, int)

    def __init__(self, initial_folder, destination_folder, source_codec, target_codec, copy_other_files):
        super().__init__()
        self.initial_folder = initial_folder
        self.destination_folder = destination_folder
        self.source_codec = source_codec
        self.target_codec = target_codec
        self.copy_other_files = copy_other_files

    def run(self):
        files_to_process = []
        ext1 = FILE_EXTENSION[self.source_codec]
        ext2 = FILE_EXTENSION[self.target_codec]
        # Gather all files that need processing.
        for root, dirs, files in os.walk(self.initial_folder):
            relative_path = os.path.relpath(root, self.initial_folder)
            out_dir = os.path.join(self.destination_folder, relative_path)
            os.makedirs(out_dir, exist_ok=True)
            for file in files:
                input_path = os.path.join(root, file)
                if file.endswith(ext1):
                    output_file = file.replace(ext1, ext2)
                    output_path = os.path.join(out_dir, output_file)
                    if not os.path.exists(output_path):
                        files_to_process.append((input_path, output_path, "transcode"))
                elif self.copy_other_files:
                    output_path = os.path.join(out_dir, file)
                    if not os.path.exists(output_path):
                        files_to_process.append((input_path, output_path, "copy"))

        total = len(files_to_process)
        # Process each file while emitting progress.
        for idx, (input_file, output_path, mode) in enumerate(files_to_process):
            progress = int(((idx + 1) / total) * 100) if total > 0 else 100
            self.progress_signal.emit(input_file, output_path, mode, progress)
            if mode == "transcode":
                subprocess.run([
                    'ffmpeg', '-i', input_file,
                    '-acodec', CODEC_NAME[self.target_codec],
                    output_path
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif mode == "copy":
                shutil.copy2(input_file, output_path)


class PreferencesDialog(QDialog):
    """
    Dialog to configure transcoding preferences.
    """
    def __init__(self, parent=None, current_source_codec=None, current_target_codec=None,
                 current_initial_folder="", current_destination_folder="", current_copy_other_files=False):
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        self.setMinimumSize(400, 300)
        self.current_source_codec = current_source_codec
        self.current_target_codec = current_target_codec
        self.current_initial_folder = current_initial_folder
        self.current_destination_folder = current_destination_folder
        self.current_copy_other_files = current_copy_other_files
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        source_codec_label = QLabel("Source codec:")
        self.source_codec_combo = QComboBox()
        self.source_codec_combo.addItems(["flac", "wav", "mp3", "aac", "vorbis"])

        target_codec_label = QLabel("Desired codec:")
        self.target_codec_combo = QComboBox()
        self.target_codec_combo.addItems(["opus", "aac", "mp3", "flac", "vorbis"])

        initial_folder_label = QLabel("Source folder:")
        self.initial_folder_line = QLineEdit()
        self.initial_folder_browse = QPushButton("Browse")
        self.initial_folder_browse.clicked.connect(self.browse_initial_folder)

        destination_folder_label = QLabel("Destination folder:")
        self.destination_folder_line = QLineEdit()
        self.destination_folder_browse = QPushButton("Browse")
        self.destination_folder_browse.clicked.connect(self.browse_destination_folder)

        self.copy_other_files_checkbox = QCheckBox("Copy other files present along desired ones")
        self.copy_other_files_checkbox.setChecked(self.current_copy_other_files)

        folder_layout = QHBoxLayout()
        folder_layout.addWidget(self.initial_folder_line)
        folder_layout.addWidget(self.initial_folder_browse)

        dest_layout = QHBoxLayout()
        dest_layout.addWidget(self.destination_folder_line)
        dest_layout.addWidget(self.destination_folder_browse)

        buttons_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addStretch()
        buttons_layout.addWidget(ok_button)
        buttons_layout.addWidget(cancel_button)

        layout.addWidget(source_codec_label)
        layout.addWidget(self.source_codec_combo)
        layout.addWidget(target_codec_label)
        layout.addWidget(self.target_codec_combo)
        layout.addWidget(initial_folder_label)
        layout.addLayout(folder_layout)
        layout.addWidget(destination_folder_label)
        layout.addLayout(dest_layout)
        layout.addWidget(self.copy_other_files_checkbox)
        layout.addStretch()
        layout.addLayout(buttons_layout)
        self.setLayout(layout)

        if self.current_source_codec:
            index = self.source_codec_combo.findText(self.current_source_codec)
            if index >= 0:
                self.source_codec_combo.setCurrentIndex(index)
        if self.current_target_codec:
            index = self.target_codec_combo.findText(self.current_target_codec)
            if index >= 0:
                self.target_codec_combo.setCurrentIndex(index)
        self.initial_folder_line.setText(self.current_initial_folder)
        self.destination_folder_line.setText(self.current_destination_folder)

    def browse_initial_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select source folder")
        if folder:
            self.initial_folder_line.setText(folder)

    def browse_destination_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select destination folder")
        if folder:
            self.destination_folder_line.setText(folder)


class InfoDialog(QDialog):
    """
    Simple information dialog.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Info")
        self.setMinimumSize(300, 200)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        info_label = QLabel("BulkTranscode\n\nMusic transcoding software.\nVersion 0.55")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)
        self.setLayout(layout)


class MainWindow(QMainWindow):
    """
    Main application window that displays the progress of the transcoding process.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BulkTranscode")
        self.setMinimumSize(800, 600)
        self.source_codec = None
        self.target_codec = None
        self.initial_folder = ""
        self.destination_folder = ""
        self.copy_other_files = False
        self.worker = None
        self.init_ui()

    def init_ui(self):
        menu_bar = self.menuBar()
        preferences_action = QAction("Preferences", self)
        preferences_action.triggered.connect(self.open_preferences)
        info_action = QAction("Info", self)
        info_action.triggered.connect(self.open_info)
        file_menu = menu_bar.addMenu("File")
        file_menu.addAction(preferences_action)
        file_menu.addAction(info_action)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.start_button = QPushButton("Start Bulk Transcode")
        self.start_button.clicked.connect(self.start_transcoding)
        layout.addWidget(self.start_button)

        # Progress table with three columns.
        self.progress_table = QTableWidget(0, 3)
        self.progress_table.setHorizontalHeaderLabels(["Input File", "Mode", "Output File"])
        self.progress_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.progress_table)

        layout.addStretch()
        self.setStatusBar(QStatusBar(self))

    def open_preferences(self):
        dialog = PreferencesDialog(
            self, self.source_codec, self.target_codec,
            self.initial_folder, self.destination_folder, self.copy_other_files
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.source_codec = dialog.source_codec_combo.currentText()
            self.target_codec = dialog.target_codec_combo.currentText()
            self.initial_folder = dialog.initial_folder_line.text()
            self.destination_folder = dialog.destination_folder_line.text()
            self.copy_other_files = dialog.copy_other_files_checkbox.isChecked()
            print("Preferences updated:")
            print("Source codec:", self.source_codec)
            print("Target codec:", self.target_codec)
            print("Initial folder:", self.initial_folder)
            print("Destination folder:", self.destination_folder)
            print("Copy other files:", self.copy_other_files)

    def open_info(self):
        dialog = InfoDialog(self)
        dialog.exec()

    def start_transcoding(self):
        if not all([self.source_codec, self.target_codec, self.initial_folder, self.destination_folder]):
            QMessageBox.warning(self, "Error", "Please set all preferences in File -> Preferences.")
            return

        self.start_button.setEnabled(False)
        self.progress_table.setRowCount(0)

        self.worker = TranscodeWorker(
            self.initial_folder, self.destination_folder,
            self.source_codec, self.target_codec, self.copy_other_files
        )
        self.worker.progress_signal.connect(self.update_progress)
        self.worker.finished.connect(self.transcoding_finished)
        self.worker.start()

    def update_progress(self, input_file, output_file, mode, progress):
        """
        Updates the progress table and the status bar with the current file being processed and overall progress.
        """
        input_name = os.path.basename(input_file)
        output_name = os.path.basename(output_file)
        row = self.progress_table.rowCount()
        self.progress_table.insertRow(row)
        self.progress_table.setItem(row, 0, QTableWidgetItem(input_name))

        mode_text = "Transcode" if mode == "transcode" else "Copy"
        mode_item = QTableWidgetItem(mode_text)
        mode_item.setForeground(QColor("green") if mode == "transcode" else QColor("blue"))
        self.progress_table.setItem(row, 1, mode_item)

        self.progress_table.setItem(row, 2, QTableWidgetItem(output_name))
        self.statusBar().showMessage(f"Progress: {progress}%")

    def transcoding_finished(self):
        self.start_button.setEnabled(True)
        QMessageBox.information(self, "Finished", "Transcoding completed.")


def run_gui():
    """
    Launches the GUI application.
    """
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BulkTranscode - Transcode audio files recursively")
    parser.add_argument("--source-codec", choices=["aac", "flac", "opus", "mp3", "vorbis"],
                        help="Source codec")
    parser.add_argument("--target-codec", choices=["aac", "flac", "opus", "mp3", "vorbis"],
                        help="Target codec")
    parser.add_argument("--initial-folder", help="Folder containing source audio files")
    parser.add_argument("--destination-folder", help="Folder to output transcoded audio files")
    parser.add_argument("--copy-others", action="store_true",
                        help="Copy files that do not match the source codec extension")
    args = parser.parse_args()

    # Command-line mode if all parameters are provided.
    if args.source_codec and args.target_codec and args.initial_folder and args.destination_folder:
        print("Running in command-line mode with the following parameters:")
        print("Source codec:", args.source_codec)
        print("Target codec:", args.target_codec)
        print("Initial folder:", args.initial_folder)
        print("Destination folder:", args.destination_folder)
        print("Copy other files:", args.copy_others)
        ext1 = FILE_EXTENSION[args.source_codec]
        ext2 = FILE_EXTENSION[args.target_codec]
        files_to_process = []
        for root, dirs, files in os.walk(args.initial_folder):
            relative_path = os.path.relpath(root, args.initial_folder)
            out_dir = os.path.join(args.destination_folder, relative_path)
            os.makedirs(out_dir, exist_ok=True)
            for file in files:
                input_path = os.path.join(root, file)
                if file.endswith(ext1):
                    output_file = file.replace(ext1, ext2)
                    output_path = os.path.join(out_dir, output_file)
                    if not os.path.exists(output_path):
                        files_to_process.append((input_path, output_path, "transcode"))
                elif args.copy_others:
                    output_path = os.path.join(out_dir, file)
                    if not os.path.exists(output_path):
                        files_to_process.append((input_path, output_path, "copy"))
        total = len(files_to_process)
        for idx, (input_file, output_path, mode) in enumerate(files_to_process):
            progress = int(((idx + 1) / total) * 100) if total > 0 else 100
            if mode == "transcode":
                print(f"Transcoding: {os.path.basename(input_file)} -> {os.path.basename(output_path)} ({progress}%)")
                subprocess.run([
                    'ffmpeg', '-i', input_file,
                    '-acodec', CODEC_NAME[args.target_codec],
                    output_path
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif mode == "copy":
                print(f"Copying: {os.path.basename(input_file)} -> {os.path.basename(output_path)} ({progress}%)")
                shutil.copy2(input_file, output_path)
        print("Transcoding completed.")
    else:
        run_gui()

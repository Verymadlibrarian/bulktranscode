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

# Dictionaries for codec names and file extensions
name = {
    "aac": "aac",
    "flac": "flac",
    "opus": "libopus",
    "mp3": "libmp3lame",
    "vorbis": "libvorbis",
}

extension = {
    "aac": ".aac",
    "flac": ".flac",
    "opus": ".opus",
    "mp3": ".mp3",
    "vorbis": ".ogg",
}

class TranscodeWorker(QThread):
    # Now emitting input_file, output_file, and mode ("transcode" or "copy")
    progress_signal = pyqtSignal(str, str, str)

    def __init__(self, initial_folder, destination_folder, source_codec, target_codec, copy_other_files):
        super().__init__()
        self.initial_folder = initial_folder
        self.destination_folder = destination_folder
        self.source_codec = source_codec
        self.target_codec = target_codec
        self.copy_other_files = copy_other_files

    def run(self):
        # Build a list of files to process
        files_to_process = []
        ext1 = extension[self.source_codec]
        ext2 = extension[self.target_codec]
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
        
        # Process each file and emit progress before handling it
        for input_file, output_path, mode in files_to_process:
            self.progress_signal.emit(input_file, output_path, mode)
            if mode == "transcode":
                subprocess.run([
                    'ffmpeg', '-i', input_file,
                    '-acodec', name[self.target_codec],
                    output_path
                ])
            elif mode == "copy":
                shutil.copy2(input_file, output_path)

class PreferencesDialog(QDialog):
    def __init__(self, parent=None, current_source_codec=None, current_target_codec=None,
                 current_initial_folder="", current_destination_folder="", current_copy_other_files=False):
        super().__init__(parent)
        self.setWindowTitle("Préférences")
        self.setMinimumSize(400, 300)
        self.current_source_codec = current_source_codec
        self.current_target_codec = current_target_codec
        self.current_initial_folder = current_initial_folder
        self.current_destination_folder = current_destination_folder
        self.current_copy_other_files = current_copy_other_files
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Source codec selection
        source_codec_label = QLabel("Codec source:")
        self.source_codec_combo = QComboBox()
        self.source_codec_combo.addItems(["flac", "wav", "mp3", "aac", "vorbis"])

        # Target codec selection
        target_codec_label = QLabel("Codec cible:")
        self.target_codec_combo = QComboBox()
        self.target_codec_combo.addItems(["opus", "aac", "mp3", "flac", "vorbis"])

        # Source folder selection
        initial_folder_label = QLabel("Dossier source:")
        self.initial_folder_line = QLineEdit()
        self.initial_folder_browse = QPushButton("Parcourir")
        self.initial_folder_browse.clicked.connect(self.browse_initial_folder)

        # Destination folder selection
        destination_folder_label = QLabel("Dossier destination:")
        self.destination_folder_line = QLineEdit()
        self.destination_folder_browse = QPushButton("Parcourir")
        self.destination_folder_browse.clicked.connect(self.browse_destination_folder)

        # Copy files that are not the codec extension
        self.copy_other_files_checkbox = QCheckBox("Copier les fichiers autre que l'extension [codec]")
        self.copy_other_files_checkbox.setChecked(self.current_copy_other_files)
        
        # Layout for folder selections
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(self.initial_folder_line)
        folder_layout.addWidget(self.initial_folder_browse)

        dest_layout = QHBoxLayout()
        dest_layout.addWidget(self.destination_folder_line)
        dest_layout.addWidget(self.destination_folder_browse)

        # Buttons layout
        buttons_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Annuler")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addStretch()
        buttons_layout.addWidget(ok_button)
        buttons_layout.addWidget(cancel_button)

        # Assemble the layout
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

        # Pre-populate fields if values exist
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
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Info")
        self.setMinimumSize(300, 200)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        info_label = QLabel("BulkTranscode\n\Music transcoding software.\nVersion 0.55")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)
        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BulkTranscode")
        self.setMinimumSize(800, 600)
        # Preferences variables
        self.source_codec = None
        self.target_codec = None
        self.initial_folder = ""
        self.destination_folder = ""
        self.copy_other_files = False
        self.worker = None
        self.init_ui()

    def init_ui(self):
        # Menu bar
        menu_bar = self.menuBar()
        preferences_action = QAction("Preferences", self)
        preferences_action.triggered.connect(self.open_preferences)
        info_action = QAction("Info", self)
        info_action.triggered.connect(self.open_info)
        file_menu = menu_bar.addMenu("File")
        file_menu.addAction(preferences_action)
        file_menu.addAction(info_action)

        # Central widget with a layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Start transcoding button
        self.start_button = QPushButton("Start Bulk Transcode")
        self.start_button.clicked.connect(self.start_transcoding)
        layout.addWidget(self.start_button)

        # Progress grid: now with three columns: Input File, Mode, Output File
        self.progress_table = QTableWidget(0, 3)
        self.progress_table.setHorizontalHeaderLabels(["Input File", "Mode", "Output File"])
        self.progress_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.progress_table)

        layout.addStretch()
        self.setStatusBar(QStatusBar(self))

    def open_preferences(self):
        dialog = PreferencesDialog(self, self.source_codec, self.target_codec,
                                   self.initial_folder, self.destination_folder, self.copy_other_files)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.source_codec = dialog.source_codec_combo.currentText()
            self.target_codec = dialog.target_codec_combo.currentText()
            self.initial_folder = dialog.initial_folder_line.text()
            self.destination_folder = dialog.destination_folder_line.text()
            self.copy_other_files = dialog.copy_other_files_checkbox.isChecked()  # <-- Here
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
            QMessageBox.warning(self, "Erreur", "Please set all preferences in File -> Préférences.")
            return

        # Disable the button to prevent re-entry and clear previous progress
        self.start_button.setEnabled(False)
        self.progress_table.setRowCount(0)

        # Create and start the worker thread
        self.worker = TranscodeWorker(self.initial_folder,
                                      self.destination_folder,
                                      self.source_codec,
                                      self.target_codec,
                                      self.copy_other_files)
        self.worker.progress_signal.connect(self.update_progress)
        self.worker.finished.connect(self.transcoding_finished)
        self.worker.start()

    def update_progress(self, input_file, output_file, mode):
        # Display only the filename and separate the mode into its own column with color
        input_name = os.path.basename(input_file)
        output_name = os.path.basename(output_file)
        row = self.progress_table.rowCount()
        self.progress_table.insertRow(row)

        # Input File column
        self.progress_table.setItem(row, 0, QTableWidgetItem(input_name))
        
        # Mode column: create an item and set its text color
        mode_item = QTableWidgetItem("Transcode" if mode == "transcode" else "Copy")
        if mode == "transcode":
            mode_item.setForeground(QColor("green"))
        else:
            mode_item.setForeground(QColor("blue"))
        self.progress_table.setItem(row, 1, mode_item)
        
        # Output File column
        self.progress_table.setItem(row, 2, QTableWidgetItem(output_name))

    def transcoding_finished(self):
        self.start_button.setEnabled(True)
        QMessageBox.information(self, "Terminé", "Transcodage terminé.")

def run_gui():
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

    # Command-line mode if all parameters are provided
    if args.source_codec and args.target_codec and args.initial_folder and args.destination_folder:
        print("Running in command-line mode with the following parameters:")
        print("Source codec:", args.source_codec)
        print("Target codec:", args.target_codec)
        print("Initial folder:", args.initial_folder)
        print("Destination folder:", args.destination_folder)
        print("Copy other files:", args.copy_others)
        ext1 = extension[args.source_codec]
        ext2 = extension[args.target_codec]
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
                        print(f"Transcoding: {os.path.basename(input_path)} -> {os.path.basename(output_path)}")
                        subprocess.run([
                            'ffmpeg', '-i', input_path,
                            '-acodec', name[args.target_codec],
                            output_path
                        ])
                elif args.copy_others:
                    output_path = os.path.join(out_dir, file)
                    if not os.path.exists(output_path):
                        print(f"Copying: {os.path.basename(input_path)} -> {os.path.basename(output_path)}")
                        shutil.copy2(input_path, output_path)
        print("Transcoding completed.")
    else:
        run_gui()

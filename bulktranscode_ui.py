import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QDialog, QWidget, QLabel,
    QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QComboBox,
    QFileDialog, QStatusBar, QMessageBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QCheckBox
)
from PyQt6.QtGui import QAction, QColor
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from bulktranscode_core import gather_files, process_file

class TranscodeWorkerUI(QThread):
    """
    Worker thread for the UI that processes files and emits progress signals.
    """
    progress_signal = pyqtSignal(str, str, str, int)

    def __init__(self, source_folder, destination_folder, source_codec, target_codec, copy_other_files):
        super().__init__()
        self.source_folder = source_folder
        self.destination_folder = destination_folder
        self.source_codec = source_codec
        self.target_codec = target_codec
        self.copy_other_files = copy_other_files

    def run(self):
        files_to_process = gather_files(
            self.source_folder, self.destination_folder,
            self.source_codec, self.target_codec, self.copy_other_files
        )
        total = len(files_to_process)
        for idx, (input_file, output_file, mode) in enumerate(files_to_process):
            progress = int(((idx + 1) / total) * 100) if total > 0 else 100
            self.progress_signal.emit(input_file, output_file, mode, progress)
            process_file(input_file, output_file, mode, self.target_codec)

class PreferencesDialog(QDialog):
    """
    Dialog for setting transcoding preferences.
    """
    def __init__(self, parent=None, current_source_codec=None, current_target_codec=None,
                 current_source_folder="", current_destination_folder="", current_copy_other_files=False):
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        self.setMinimumSize(400, 300)
        self.current_source_codec = current_source_codec
        self.current_target_codec = current_target_codec
        self.current_source_folder = current_source_folder
        self.current_destination_folder = current_destination_folder
        self.current_copy_other_files = current_copy_other_files
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        source_codec_label = QLabel("Source codec:")
        self.source_codec_combo = QComboBox()
        self.source_codec_combo.addItems(["aac", "flac", "mp3", "opus", "vorbis"])

        target_codec_label = QLabel("Desired codec:")
        self.target_codec_combo = QComboBox()
        self.target_codec_combo.addItems(["aac", "flac", "mp3", "opus", "vorbis"])

        source_folder_label = QLabel("Source folder:")
        self.source_folder_line = QLineEdit()
        self.source_folder_browse = QPushButton("Browse")
        self.source_folder_browse.clicked.connect(self.browse_source_folder)

        destination_folder_label = QLabel("Destination folder:")
        self.destination_folder_line = QLineEdit()
        self.destination_folder_browse = QPushButton("Browse")
        self.destination_folder_browse.clicked.connect(self.browse_destination_folder)

        self.copy_other_files_checkbox = QCheckBox("Copy other files present along desired ones")
        self.copy_other_files_checkbox.setChecked(self.current_copy_other_files)

        folder_layout = QHBoxLayout()
        folder_layout.addWidget(self.source_folder_line)
        folder_layout.addWidget(self.source_folder_browse)

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
        layout.addWidget(source_folder_label)
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
        self.source_folder_line.setText(self.current_source_folder)
        self.destination_folder_line.setText(self.current_destination_folder)

    def browse_source_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select source folder")
        if folder:
            self.source_folder_line.setText(folder)

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
        info_label = QLabel("BulkTranscode\n\nMusic transcoding software.\nVersion 0.6")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)
        self.setLayout(layout)

class MainWindow(QMainWindow):
    """
    Main application window that displays transcoding progress.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BulkTranscode")
        self.setMinimumSize(800, 600)
        self.source_codec = None
        self.target_codec = None
        self.source_folder = ""
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

        self.progress_table = QTableWidget(0, 3)
        self.progress_table.setHorizontalHeaderLabels(["Input File", "Mode", "Output File"])
        self.progress_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.progress_table)

        layout.addStretch()
        self.setStatusBar(QStatusBar(self))

    def open_preferences(self):
        dialog = PreferencesDialog(
            self, self.source_codec, self.target_codec,
            self.source_folder, self.destination_folder, self.copy_other_files
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.source_codec = dialog.source_codec_combo.currentText()
            self.target_codec = dialog.target_codec_combo.currentText()
            self.source_folder = dialog.source_folder_line.text()
            self.destination_folder = dialog.destination_folder_line.text()
            self.copy_other_files = dialog.copy_other_files_checkbox.isChecked()
            print("Preferences updated:")
            print("Source codec:", self.source_codec)
            print("Target codec:", self.target_codec)
            print("source folder:", self.source_folder)
            print("Destination folder:", self.destination_folder)
            print("Copy other files:", self.copy_other_files)

    def open_info(self):
        dialog = InfoDialog(self)
        dialog.exec()

    def start_transcoding(self):
        if not all([self.source_codec, self.target_codec, self.source_folder, self.destination_folder]):
            QMessageBox.warning(self, "Error", "Please set all preferences in File -> Preferences.")
            return

        self.start_button.setEnabled(False)
        self.progress_table.setRowCount(0)

        self.worker = TranscodeWorkerUI(
            self.source_folder, self.destination_folder,
            self.source_codec, self.target_codec, self.copy_other_files
        )
        self.worker.progress_signal.connect(self.update_progress)
        self.worker.finished.connect(self.transcoding_finished)
        self.worker.start()

    def update_progress(self, input_file, output_file, mode, progress):
        """
        Updates the progress table and the status bar with the current file and overall progress.
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
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run_gui()

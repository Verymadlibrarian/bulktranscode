import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QDialog, QWidget, QLabel,
    QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QComboBox,
    QFileDialog, QStatusBar
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt

class PreferencesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Préférences")
        self.setMinimumSize(400, 300)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Sélection du codec source
        source_codec_label = QLabel("Codec source :")
        self.source_codec_combo = QComboBox()
        self.source_codec_combo.addItems(["flac", "wav", "mp3"])

        # Sélection du codec cible
        target_codec_label = QLabel("Codec cible :")
        self.target_codec_combo = QComboBox()
        self.target_codec_combo.addItems(["opus", "aac", "mp3"])

        # Sélection du dossier source
        initial_folder_label = QLabel("Dossier source :")
        self.initial_folder_line = QLineEdit()
        self.initial_folder_browse = QPushButton("Parcourir")
        self.initial_folder_browse.clicked.connect(self.browse_initial_folder)

        # Sélection du dossier destination
        destination_folder_label = QLabel("Dossier destination :")
        self.destination_folder_line = QLineEdit()
        self.destination_folder_browse = QPushButton("Parcourir")
        self.destination_folder_browse.clicked.connect(self.browse_destination_folder)

        # Layout pour le dossier source
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(self.initial_folder_line)
        folder_layout.addWidget(self.initial_folder_browse)

        # Layout pour le dossier destination
        dest_layout = QHBoxLayout()
        dest_layout.addWidget(self.destination_folder_line)
        dest_layout.addWidget(self.destination_folder_browse)

        # Boutons OK et Annuler
        buttons_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Annuler")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addStretch()
        buttons_layout.addWidget(ok_button)
        buttons_layout.addWidget(cancel_button)

        # Ajout des widgets dans le layout principal
        layout.addWidget(source_codec_label)
        layout.addWidget(self.source_codec_combo)
        layout.addWidget(target_codec_label)
        layout.addWidget(self.target_codec_combo)
        layout.addWidget(initial_folder_label)
        layout.addLayout(folder_layout)
        layout.addWidget(destination_folder_label)
        layout.addLayout(dest_layout)
        layout.addStretch()
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def browse_initial_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Sélectionnez le dossier source")
        if folder:
            self.initial_folder_line.setText(folder)

    def browse_destination_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Sélectionnez le dossier destination")
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
        info_label = QLabel("BulkTranscode\n\nLogiciel de transcodage de musique.\nVersion 1.0")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)
        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BulkTranscode")
        self.setMinimumSize(800, 600)
        self.init_ui()

    def init_ui(self):
        # Création de la barre de menus
        menu_bar = self.menuBar()

        # Action pour Préférences
        preferences_action = QAction("Préférences", self)
        preferences_action.triggered.connect(self.open_preferences)

        # Action pour Info
        info_action = QAction("Info", self)
        info_action.triggered.connect(self.open_info)

        # Ajout des actions dans un menu (par exemple "Fichier")
        file_menu = menu_bar.addMenu("Fichier")
        file_menu.addAction(preferences_action)
        file_menu.addAction(info_action)

        # Widget central vide pour pouvoir être ajusté ultérieurement
        self.setCentralWidget(QWidget())

        # Barre de statut
        self.setStatusBar(QStatusBar(self))

    def open_preferences(self):
        dialog = PreferencesDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Récupération des préférences sélectionnées
            source_codec = dialog.source_codec_combo.currentText()
            target_codec = dialog.target_codec_combo.currentText()
            initial_folder = dialog.initial_folder_line.text()
            destination_folder = dialog.destination_folder_line.text()
            # Ici, vous pouvez stocker ou utiliser ces valeurs
            print("Préférences sélectionnées :")
            print("Codec source :", source_codec)
            print("Codec cible  :", target_codec)
            print("Dossier source :", initial_folder)
            print("Dossier destination :", destination_folder)

    def open_info(self):
        dialog = InfoDialog(self)
        dialog.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

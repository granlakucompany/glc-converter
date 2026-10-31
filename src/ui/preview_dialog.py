"""
GLC CONVERTER — Lecteur et Prévisualisation Média
Éditeur: GRAN LAKU COMPANY | https://granlaku.com/glcconverter
"""
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QTextEdit
)
from PySide6.QtGui import QPixmap
from ..core.mime_detector import MimeDetector

class PreviewDialog(QDialog):
    """Affiche une prévisualisation rapide et les métadonnées techniques du fichier."""

    def __init__(self, filepath: str, parent=None):
        super().__init__(parent)
        self.filepath = filepath
        self.setWindowTitle(f"Prévisualisation — {Path(filepath).name}")
        self.resize(600, 500)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        info = MimeDetector.identify_file(self.filepath)
        cat = info.get("category", "")

        # Zone d'image si média visuel
        if cat == "image":
            lbl_img = QLabel()
            lbl_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_img.setStyleSheet("background-color: #0b0914; border-radius: 8px; padding: 10px;")
            pix = QPixmap(self.filepath)
            if not pix.isNull():
                lbl_img.setPixmap(pix.scaled(550, 300, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            layout.addWidget(lbl_img)

        # Rapport de métadonnées
        txt_meta = QTextEdit()
        txt_meta.setReadOnly(True)
        txt_meta.setStyleSheet("background-color: #120e24; color: #a78bfa; font-family: monospace;")
        
        lines = [
            f"Fichier : {info.get('filename')}",
            f"Chemin  : {info.get('path')}",
            f"Taille  : {info.get('size_formatted')} ({info.get('size_bytes')} octets)",
            f"MIME    : {info.get('mime_type')}",
            f"Groupe  : {info.get('category').upper()}",
            "--------------------------------------------------"
        ]
        
        meta = info.get("metadata", {})
        for k, v in meta.items():
            lines.append(f"{k.ljust(15)}: {v}")

        txt_meta.setText("\n".join(lines))
        layout.addWidget(txt_meta)

        btn_close = QPushButton("Fermer")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

"""
GLC CONVERTER — Dialogue de Conversion HTML/Animation vers Vraie Vidéo
Éditeur: GRAN LAKU COMPANY | https://granlaku.com/glcconverter
"""
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSpinBox, QComboBox, QFileDialog, QGroupBox
)
from ..core.html_detector import HtmlDetector
from ..core.settings_manager import get_last_open_dir, set_last_open_dir

class HtmlToVideoDialog(QDialog):
    """Boîte de dialogue permettant de configurer la conversion d'animations web en vidéo."""

    def __init__(self, parent=None, initial_path: str = ""):
        super().__init__(parent)
        self.setWindowTitle("Conversion HTML / XML / Animation vers Vraie Vidéo — GLC Studio")
        self.resize(580, 420)
        self.initial_path = initial_path
        self._audio_path = None
        self._setup_ui()
        if self.initial_path:
            self._on_source_changed(self.initial_path)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        # En-tête informatif
        header = QLabel("⚡ Moteur Déterministe d'Horloge Virtuelle & Audio")
        header.setStyleSheet("font-size: 16px; font-weight: 800; color: #fbbf24;")
        layout.addWidget(header)

        desc = QLabel(
            "Convertit n'importe quel composant HTML5, Kadans, Three.js ou animation CSS "
            "en vidéo haute définition avec synchronisation audio native sans coupure."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #a78bfa; font-size: 12px;")
        layout.addWidget(desc)

        # Fichier source
        src_group = QGroupBox("Source HTML / XML")
        src_layout = QVBoxLayout(src_group)
        h_src = QHBoxLayout()
        self.txt_source = QLineEdit(self.initial_path)
        self.txt_source.setPlaceholderText("Chemin vers un fichier .html ou .xml...")
        self.txt_source.textChanged.connect(self._on_source_changed)
        h_src.addWidget(self.txt_source)

        btn_browse = QPushButton("📁 Parcourir")
        btn_browse.clicked.connect(self._browse)
        h_src.addWidget(btn_browse)
        src_layout.addLayout(h_src)

        # Indicateur de détection audio & métadonnées
        self.lbl_detected_info = QLabel("ℹ️ Sélectionnez un composant HTML pour détecter durée, résolution et voix.")
        self.lbl_detected_info.setStyleSheet("color: #38bdf8; font-size: 11px;")
        self.lbl_detected_info.setWordWrap(True)
        src_layout.addWidget(self.lbl_detected_info)

        layout.addWidget(src_group)

        # Paramètres de rendu
        cfg_group = QGroupBox("Paramètres de Rendu Vidéo")
        cfg_layout = QVBoxLayout(cfg_group)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Résolution:"))
        self.cb_resolution = QComboBox()
        self.cb_resolution.addItems([
            "1920x1080 (Full HD 16:9)",
            "1080x1920 (Vertical 9:16 Shorts/Reels)",
            "3840x2160 (4K UHD)",
            "2160x3840 (Vertical 4K)",
            "1280x720 (HD)",
            "1080x1080 (Carré 1:1)",
            "7680x4320 (8K UHD)",
            "11520x6480 (12K UHD)",
            "12288x6480 (12K DCI Cinema)"
        ])
        row1.addWidget(self.cb_resolution)

        row1.addWidget(QLabel("Cadence (FPS):"))
        self.sp_fps = QSpinBox()
        self.sp_fps.setRange(15, 120)
        self.sp_fps.setValue(30)
        row1.addWidget(self.sp_fps)
        cfg_layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Durée de capture (sec):"))
        self.sp_duration = QSpinBox()
        self.sp_duration.setRange(1, 3600)
        self.sp_duration.setValue(5)
        row2.addWidget(self.sp_duration)

        row2.addWidget(QLabel("Format Cible:"))
        self.cb_format = QComboBox()
        self.cb_format.addItems(["MP4 (H.264 + AAC)", "MOV (ProRes + AAC)", "WebM (VP9 + Opus)"])
        row2.addWidget(self.cb_format)
        cfg_layout.addLayout(row2)

        layout.addWidget(cfg_group)

        # Boutons d'action
        btn_box = QHBoxLayout()
        btn_box.addStretch()

        btn_cancel = QPushButton("Annuler")
        btn_cancel.clicked.connect(self.reject)
        btn_box.addWidget(btn_cancel)

        self.btn_convert = QPushButton("🚀 Lancer le Rendu Vidéo")
        self.btn_convert.setObjectName("btnPrimary")
        self.btn_convert.clicked.connect(self.accept)
        btn_box.addWidget(self.btn_convert)

        layout.addLayout(btn_box)

    def _browse(self):
        start_dir = get_last_open_dir()
        f, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner un fichier HTML ou XML animé",
            start_dir,
            "Fichiers Web & XML (*.html *.htm *.xml *.xhtml);;Tous les fichiers (*.*)"
        )
        if f:
            set_last_open_dir(f)
            self.txt_source.setText(f)

    def _on_source_changed(self, path_str: str):
        path_str = path_str.strip()
        if not path_str or not Path(path_str).exists():
            return
        set_last_open_dir(path_str)

        try:
            meta = HtmlDetector.detect_html_metadata(path_str)
            dur = meta.get("duration", 5.0)
            w = meta.get("width", 1920)
            h = meta.get("height", 1080)
            fps = meta.get("fps", 30)
            audio = meta.get("audio_path")
            self._audio_path = audio

            # Appliquer la durée et le framerate détectés
            self.sp_duration.setValue(max(1, int(round(dur))))
            self.sp_fps.setValue(fps)

            # Sélectionner la résolution correspondante
            target_res_prefix = f"{w}x{h}"
            found_idx = -1
            for i in range(self.cb_resolution.count()):
                if self.cb_resolution.itemText(i).startswith(target_res_prefix):
                    found_idx = i
                    break
            if found_idx >= 0:
                self.cb_resolution.setCurrentIndex(found_idx)
            else:
                custom_item = f"{w}x{h} (Détecté)"
                self.cb_resolution.insertItem(0, custom_item)
                self.cb_resolution.setCurrentIndex(0)

            # Mettre à jour le texte descriptif de détection
            audio_msg = f"🎵 Audio/Voix: {Path(audio).name}" if audio else "🔇 Audio: Muet (aucun fichier audio)"
            self.lbl_detected_info.setText(
                f"✅ Détection auto : Durée {dur:.1f}s | Format {w}x{h} ({fps} FPS) | {audio_msg}"
            )
        except Exception as e:
            self.lbl_detected_info.setText(f"ℹ️ Erreur détection: {e}")

    def get_config(self) -> dict:
        res_str = self.cb_resolution.currentText().split()[0]
        w, h = res_str.split("x")
        fmt = "mp4"
        if "MOV" in self.cb_format.currentText(): fmt = "mov"
        elif "WebM" in self.cb_format.currentText(): fmt = "webm"

        src_val = self.txt_source.text().strip()
        return {
            "source_path": src_val,
            "url": src_val,
            "width": int(w),
            "height": int(h),
            "fps": self.sp_fps.value(),
            "duration": float(self.sp_duration.value()),
            "format": fmt,
            "audio_path": self._audio_path
        }

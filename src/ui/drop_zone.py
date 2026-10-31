"""
GLC CONVERTER — Étape 1 : Zone d'Importation Didactique (Drop Zone)
Éditeur: GRAN LAKU COMPANY | https://granlaku.com/glcconverter
"""
from pathlib import Path
from typing import List
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFileDialog
)
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QPixmap
from ..config import LOGO_PATH
from ..core.i18n import I18nManager, tr
from ..core.settings_manager import get_last_open_dir, set_last_open_dir

class DropZoneWidget(QFrame):
    """Zone interactive didactique de glisser-déposer (Étape 1 du workflow)."""

    files_dropped = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("dropZone")
        self.setAcceptDrops(True)
        self._setup_ui()
        self.retranslate_ui()
        I18nManager.get_instance().register_listener(self.retranslate_ui)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(5)
        layout.setContentsMargins(10, 8, 10, 8)

        # Badge Numéro d'Étape Didactique
        self.lbl_step = QLabel(tr("step1_title"))
        self.lbl_step.setObjectName("stepBadge")
        self.lbl_step.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_step)

        # Icône centrale avec logo officiel haute résolution équilibré (54x54)
        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if LOGO_PATH.exists():
            pix = QPixmap(str(LOGO_PATH)).scaled(54, 54, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.icon_label.setPixmap(pix)
        else:
            self.icon_label.setText("📥")
            self.icon_label.setStyleSheet("font-size: 38px; color: #7c3aed;")
        layout.addWidget(self.icon_label)

        # Titre d'invitation clair
        self.title_label = QLabel(tr("drop_title"))
        self.title_label.setObjectName("dropTitle")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        # Sous-titre rassurant
        self.sub_label = QLabel(tr("drop_sub"))
        self.sub_label.setObjectName("dropSub")
        self.sub_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.sub_label)

        # Boutons d'ajout responsive et évidents
        btn_box = QHBoxLayout()
        btn_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_box.setSpacing(6)

        self.btn_browse = QPushButton("📄 Fichiers")
        self.btn_browse.setObjectName("btnBrowse")
        self.btn_browse.setToolTip(tr("browse_tooltip"))
        self.btn_browse.clicked.connect(self._browse_files)
        btn_box.addWidget(self.btn_browse)

        self.btn_folder = QPushButton("📁 Dossier")
        self.btn_folder.setObjectName("btnFolder")
        self.btn_folder.setToolTip(tr("folder_tooltip"))
        self.btn_folder.clicked.connect(self._browse_folder)
        btn_box.addWidget(self.btn_folder)

        self.btn_link = QPushButton(tr("browse_link"))
        self.btn_link.setObjectName("btnLink")
        self.btn_link.setToolTip(tr("link_tooltip"))
        self.btn_link.clicked.connect(self._browse_link)
        btn_box.addWidget(self.btn_link)

        layout.addLayout(btn_box)

    def retranslate_ui(self, lang_code: str = None):
        """Met à jour instantanément tous les textes dans la langue active."""
        self.lbl_step.setText(tr("step1_title"))
        self.title_label.setText(tr("drop_title"))
        self.sub_label.setText(tr("drop_sub"))
        # Libellés courts avec icônes garantis sans troncature
        cur_lang = (lang_code or getattr(I18nManager.get_instance(), "current_lang", "fr")).lower()
        if "ht" in cur_lang:
            self.btn_browse.setText("📄 Fichye")
            self.btn_folder.setText("📁 Dosye")
        elif "en" in cur_lang:
            self.btn_browse.setText("📄 Files")
            self.btn_folder.setText("📁 Folder")
        elif "es" in cur_lang:
            self.btn_browse.setText("📄 Archivos")
            self.btn_folder.setText("📁 Carpeta")
        elif "pt" in cur_lang:
            self.btn_browse.setText("📄 Arquivos")
            self.btn_folder.setText("📁 Pasta")
        else:
            self.btn_browse.setText("📄 Fichiers")
            self.btn_folder.setText("📁 Dossier")
        self.btn_link.setText(tr("browse_link"))
        self.btn_browse.setToolTip(tr("browse_tooltip"))
        self.btn_folder.setToolTip(tr("folder_tooltip"))
        self.btn_link.setToolTip(tr("link_tooltip"))

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls() or event.mimeData().hasText():
            event.acceptProposedAction()
            self.setProperty("dragActive", True)
            self.style().unpolish(self)
            self.style().polish(self)

    def dragLeaveEvent(self, event):
        self.setProperty("dragActive", False)
        self.style().unpolish(self)
        self.style().polish(self)

    def dropEvent(self, event: QDropEvent):
        self.setProperty("dragActive", False)
        self.style().unpolish(self)
        self.style().polish(self)

        files = []
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                local_path = url.toLocalFile()
                if local_path:
                    p = Path(local_path)
                    if p.is_file():
                        files.append(str(p))
                    elif p.is_dir():
                        for item in p.rglob("*"):
                            if item.is_file():
                                files.append(str(item))
                else:
                    raw_str = url.toString()
                    if raw_str.startswith("http://") or raw_str.startswith("https://"):
                        files.append(raw_str)
        elif event.mimeData().hasText():
            text = event.mimeData().text().strip()
            if text.startswith("http://") or text.startswith("https://") or text.startswith("file://") or Path(text).exists():
                if text.startswith("file://"):
                    from PySide6.QtCore import QUrl
                    lp = QUrl(text).toLocalFile()
                    if lp and Path(lp).exists():
                        text = str(Path(lp).resolve())
                files.append(text)

        if files:
            set_last_open_dir(files[0])
            self.files_dropped.emit(files)

    def _browse_link(self):
        from .link_input_dialog import LocalLinkDialog
        dlg = LocalLinkDialog(self)
        if dlg.exec():
            link = dlg.get_link()
            if link:
                p = Path(link)
                if p.exists() and p.is_dir():
                    set_last_open_dir(str(p.resolve()))
                    files = [str(f) for f in p.rglob("*") if f.is_file()]
                    if files:
                        self.files_dropped.emit(files)
                else:
                    if p.exists() and p.is_file():
                        set_last_open_dir(str(p.resolve()))
                    self.files_dropped.emit([link])

    def _browse_files(self):
        filter_str = (
            "Tous les fichiers pris en charge (*.*);;"
            "Animations Web & XML (*.html *.htm *.xml *.xhtml *.json);;"
            "Vidéos (*.mp4 *.mkv *.mov *.webm *.avi *.flv *.wmv *.ts *.m2ts *.mxf);;"
            "Images (*.png *.jpg *.jpeg *.webp *.avif *.heic *.tiff *.bmp *.svg *.psd);;"
            "Audio (*.mp3 *.wav *.flac *.aac *.ogg *.opus *.m4a *.alac *.aiff);;"
            "Modèles 3D (*.obj *.stl *.gltf *.glb *.fbx *.ply);;"
            "Documents (*.pdf *.docx *.pptx *.xlsx *.txt *.md *.rtf *.epub)"
        )
        start_dir = get_last_open_dir()
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Sélectionner des fichiers à convertir",
            start_dir,
            filter_str
        )
        if files:
            set_last_open_dir(files[0])
            self.files_dropped.emit(files)

    def _browse_folder(self):
        start_dir = get_last_open_dir()
        folder = QFileDialog.getExistingDirectory(self, "Sélectionner un dossier complet", start_dir)
        if folder:
            set_last_open_dir(folder)
            p = Path(folder)
            files = [str(f) for f in p.rglob("*") if f.is_file()]
            if files:
                self.files_dropped.emit(files)

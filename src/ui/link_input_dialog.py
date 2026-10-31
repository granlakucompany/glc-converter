"""
GLC CONVERTER — Dialogue d'Ajout de Lien Local & URL Web (Kadans WASDEV / composition.html)
Éditeur: GRAN LAKU COMPANY | https://granlaku.com/glcconverter
"""
from pathlib import Path
from PySide6.QtCore import Qt, QUrl
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QApplication, QFileDialog
)
from ..core.i18n import tr
from ..core.settings_manager import get_last_open_dir, set_last_open_dir


class LocalLinkDialog(QDialog):
    """Boîte de dialogue permettant d'entrer ou coller un lien Kadans WASDEV ou charger composition.html."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("dlg_link_title"))
        self.setMinimumWidth(520)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self._link_result = ""
        self._setup_ui()
        self._check_clipboard()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(18, 16, 18, 16)

        # En-tête avec badge ou icône
        header = QHBoxLayout()
        icon_lbl = QLabel("⚡")
        icon_lbl.setStyleSheet("font-size: 22px;")
        header.addWidget(icon_lbl)

        title_lbl = QLabel(tr("dlg_link_title"))
        title_lbl.setStyleSheet("font-size: 13.5px; font-weight: 800; color: #7c3aed;")
        header.addWidget(title_lbl)
        header.addStretch()
        layout.addLayout(header)

        # Description
        desc_lbl = QLabel(tr("dlg_link_desc"))
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet("font-size: 11px; opacity: 0.85;")
        layout.addWidget(desc_lbl)

        # Champ de saisie avec bouton de parcours direct composition.html
        input_row = QHBoxLayout()
        input_row.setSpacing(6)

        self.txt_url = QLineEdit()
        self.txt_url.setPlaceholderText(tr("dlg_link_placeholder"))
        self.txt_url.setClearButtonEnabled(True)
        self.txt_url.returnPressed.connect(self._on_validate)
        input_row.addWidget(self.txt_url, stretch=1)

        self.btn_browse_comp = QPushButton(tr("dlg_link_browse_comp"))
        self.btn_browse_comp.setStyleSheet("""
            QPushButton {
                padding: 6px 10px;
                font-size: 11px;
                font-weight: 700;
            }
        """)
        self.btn_browse_comp.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_browse_comp.clicked.connect(self._browse_composition_file)
        input_row.addWidget(self.btn_browse_comp)

        layout.addLayout(input_row)

        # Suggestions rapides / raccourcis utiles (Kadans & WASDEV localhost)
        quick_box = QHBoxLayout()
        quick_box.setSpacing(6)
        lbl_quick = QLabel("Suggestions :")
        lbl_quick.setStyleSheet("font-size: 10px; color: #64748b; font-weight: 600;")
        quick_box.addWidget(lbl_quick)

        for chip_text in ["http://localhost:3000", "http://localhost:8800", "composition.html"]:
            btn_chip = QPushButton(chip_text)
            btn_chip.setStyleSheet("""
                QPushButton {
                    background: rgba(124, 58, 237, 0.1);
                    color: #7c3aed;
                    border: 1px solid rgba(124, 58, 237, 0.25);
                    border-radius: 4px;
                    padding: 2px 6px;
                    font-size: 10px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background: rgba(124, 58, 237, 0.25);
                    border-color: #7c3aed;
                }
            """)
            btn_chip.setCursor(Qt.CursorShape.PointingHandCursor)
            if chip_text == "composition.html":
                btn_chip.clicked.connect(self._browse_composition_file)
            else:
                btn_chip.clicked.connect(lambda _, t=chip_text: self.txt_url.setText(t))
            quick_box.addWidget(btn_chip)
        quick_box.addStretch()
        layout.addLayout(quick_box)

        # Boutons d'action
        btn_box = QHBoxLayout()
        btn_box.addStretch()

        self.btn_cancel = QPushButton(tr("dlg_link_cancel"))
        self.btn_cancel.clicked.connect(self.reject)
        btn_box.addWidget(self.btn_cancel)

        self.btn_open = QPushButton(tr("dlg_link_open"))
        self.btn_open.setObjectName("btnPrimary")
        self.btn_open.setDefault(True)
        self.btn_open.clicked.connect(self._on_validate)
        btn_box.addWidget(self.btn_open)

        layout.addLayout(btn_box)

    def _browse_composition_file(self):
        """Ouvre un sélecteur de fichier ciblant directement composition.html."""
        start_dir = get_last_open_dir()
        f, _ = QFileDialog.getOpenFileName(
            self,
            tr("dlg_link_browse_comp"),
            start_dir,
            "Animations Kadans & Web (composition.html *.html *.htm *.xml);;Tous les fichiers (*.*)"
        )
        if f:
            set_last_open_dir(f)
            self.txt_url.setText(f)
            self._on_validate()

    def _check_clipboard(self):
        """Vérifie si le presse-papier contient un lien ou chemin valide pour le pré-remplir."""
        try:
            cb = QApplication.clipboard()
            text = cb.text().strip() if cb else ""
            if text:
                low = text.lower()
                if low.startswith(("http://", "https://", "file://", "localhost:", "127.0.0.1:")) or Path(text).exists() or "composition.html" in low:
                    self.txt_url.setText(text)
                    self.txt_url.selectAll()
        except Exception:
            pass

    def _on_validate(self):
        val = self.txt_url.text().strip()
        if not val:
            return

        # Normalisation automatique
        # 1. Si localhost:PORT ou 127.0.0.1:PORT sans schéma -> ajouter http://
        if val.startswith("localhost:") or val.startswith("127.0.0.1:"):
            val = f"http://{val}"

        # 2. Si file:// -> convertir en chemin local si possible
        if val.startswith("file://"):
            local_p = QUrl(val).toLocalFile()
            if local_p and Path(local_p).exists():
                val = str(Path(local_p).resolve())
                set_last_open_dir(val)

        # 3. Si chemin local Windows ou Unix existant
        p = Path(val)
        if p.exists():
            val = str(p.resolve())
            set_last_open_dir(val)

        self._link_result = val
        self.accept()

    def get_link(self) -> str:
        return self._link_result

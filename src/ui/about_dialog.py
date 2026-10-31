"""
GLC CONVERTER — Dialogue À Propos & Identité Entreprise
Éditeur: GRAN LAKU COMPANY | https://granlaku.com/glcconverter
"""
from pathlib import Path
from PySide6.QtCore import Qt, QUrl
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
)
from PySide6.QtGui import QPixmap, QDesktopServices
from ..config import (
    APP_NAME, APP_SUBTITLE, APP_VERSION, COMPANY_NAME,
    COMPANY_WEBSITE, COPYRIGHT_TEXT, GITHUB_URL, LOGO_PATH
)
from ..core.hw_accel import HardwareDetector
from ..core.i18n import tr

class AboutDialog(QDialog):
    """Dialogue de présentation de l'application et de GRAN LAKU COMPANY."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{tr('about')} — {APP_NAME} ({COMPANY_NAME})")
        self.resize(520, 480)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)

        # Logo officiel
        lbl_logo = QLabel()
        lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if LOGO_PATH.exists():
            pix = QPixmap(str(LOGO_PATH)).scaled(110, 110, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            lbl_logo.setPixmap(pix)
        layout.addWidget(lbl_logo)

        # Titres
        lbl_title = QLabel(APP_NAME)
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_title.setStyleSheet("font-size: 24px; font-weight: 900; color: #ffffff;")
        layout.addWidget(lbl_title)

        lbl_sub = QLabel(tr("app_subtitle"))
        lbl_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_sub.setStyleSheet("font-size: 13px; font-weight: 600; color: #fbbf24;")
        layout.addWidget(lbl_sub)

        lbl_ver = QLabel(f"Version : {APP_VERSION}")
        lbl_ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_ver.setStyleSheet("color: #94a3b8; font-size: 11px;")
        layout.addWidget(lbl_ver)

        # Encadré Entreprise
        lbl_company = QLabel(f"Développé avec excellence par {COMPANY_NAME}")
        lbl_company.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_company.setStyleSheet("font-size: 13px; font-weight: 700; color: #a78bfa; margin-top: 6px;")
        layout.addWidget(lbl_company)

        # Bouton Web cliquable
        btn_site = QPushButton(f"🌐 Visiter le site : {COMPANY_WEBSITE.replace('https://', '')}")
        btn_site.setObjectName("btnGold")
        btn_site.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_site.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(COMPANY_WEBSITE)))
        layout.addWidget(btn_site)

        # Matériel détecté
        hw_text = HardwareDetector.get_instance().get_summary_text()
        lbl_hw = QLabel(hw_text)
        lbl_hw.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_hw.setStyleSheet("color: #64748b; font-size: 11px; margin-top: 8px;")
        layout.addWidget(lbl_hw)

        # Logiciel libre : licence MIT, code source sur GitHub
        lic_row = QHBoxLayout()
        lic_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lic_row.setSpacing(10)

        lbl_lic = QLabel(tr("about_open_source"))
        lbl_lic.setStyleSheet("color: #34d399; font-weight: 700; font-size: 11px;")
        lic_row.addWidget(lbl_lic)

        btn_act = QPushButton(tr("github_btn"))
        btn_act.setToolTip(tr("github_tooltip"))
        btn_act.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_act.setStyleSheet("""
            QPushButton {
                background: #334155;
                color: #ffffff;
                font-weight: 700;
                font-size: 11px;
                border-radius: 5px;
                padding: 3px 10px;
            }
            QPushButton:hover {
                background: #475569;
            }
        """)
        btn_act.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(GITHUB_URL)))
        lic_row.addWidget(btn_act)
        layout.addLayout(lic_row)

        # Copyright
        lbl_copy = QLabel(COPYRIGHT_TEXT)
        lbl_copy.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_copy.setStyleSheet("color: #475569; font-size: 10px; margin-top: 10px;")
        layout.addWidget(lbl_copy)

        # Bouton Fermer
        btn_close = QPushButton("✓ OK")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

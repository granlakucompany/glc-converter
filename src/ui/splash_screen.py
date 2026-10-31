"""
GLC CONVERTER — Écran de Chargement Futuriste Haute Technologie (Splash Screen)
Éditeur: GRAN LAKU COMPANY | https://granlaku.com/glcconverter
"""
import math
from pathlib import Path
from PySide6.QtCore import Qt, QTimer, Signal, QRectF
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import (
    QPainter, QColor, QPen, QBrush, QLinearGradient, QRadialGradient,
    QPixmap, QFont, QPainterPath
)

from ..config import (
    APP_NAME, APP_VERSION, COMPANY_NAME,
    LOGO_FULL_PATH, LOGO_FULL_LIGHT_PATH, LOGO_FULL_DARK_PATH, LOGO_PATH
)

class FuturisticSplashScreen(QWidget):
    """
    Écran de démarrage et de chargement holographique haute technologie :
    - Thème Sombre (défaut) : Fond noir profond avec néon mauve pulsant et confort visuel.
    - Thème Clair : Fond blanc pur avec liseré mauve électrique et jauge laser violette.
    - Logo officiel GRAN LAKU COMPANY
    - Barre laser cybernétique animée
    - Messages de progression technique pas-à-pas (GPU, 12K DCI, Moteurs natifs)
    """

    loading_finished = Signal()

    STEPS = [
        (15, "◈ [01/05] INITIALISATION DU NOYAU QUANTIQUE v" + APP_VERSION + "..."),
        (38, "◈ [02/05] SONDAGE DES ACCÉLÉRATEURS SILICIUM (NVENC / QUICK_SYNC)..."),
        (62, "◈ [03/05] DÉVERROUILLAGE PIPELINE 12K DCI CINEMA (12288×6480)..."),
        (85, "◈ [04/05] CHARGEMENT DE LA MATRICE UNIVERSELLE DES FORMATS..."),
        (100, "◈ [05/05] STUDIO PRÊT • BIENVENUE DANS " + APP_NAME + "...")
    ]

    def __init__(self, is_light_mode: bool = False):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.SplashScreen)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.resize(580, 360)
        self.is_light_mode = is_light_mode

        # Centrage sur l'écran
        self._center_on_screen()

        self.current_progress = 0
        self.target_progress = 0
        self.status_text = self.STEPS[0][1]
        self.step_index = 0
        self.pulse = 0.0

        # Chargement du logo officiel
        self.logo_pix = None
        if self.is_light_mode and LOGO_FULL_LIGHT_PATH.exists():
            logo_file = LOGO_FULL_LIGHT_PATH
        elif not self.is_light_mode and LOGO_FULL_DARK_PATH.exists():
            logo_file = LOGO_FULL_DARK_PATH
        elif LOGO_FULL_PATH.exists():
            logo_file = LOGO_FULL_PATH
        else:
            logo_file = LOGO_PATH

        if logo_file.exists():
            self.logo_pix = QPixmap(str(logo_file)).scaled(
                340, 72, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )

        # Timer d'animation fluide
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_animation)
        self.timer.start(25)

    def _center_on_screen(self):
        from PySide6.QtGui import QGuiApplication
        screen = QGuiApplication.primaryScreen()
        if screen:
            geo = screen.geometry()
            x = (geo.width() - self.width()) // 2
            y = (geo.height() - self.height()) // 2
            self.move(x, y)

    def _update_animation(self):
        self.pulse += 0.06

        # Progression incrémentale fluide
        if self.step_index < len(self.STEPS):
            target, text = self.STEPS[self.step_index]
            self.status_text = text
            if self.current_progress < target:
                self.current_progress += 1.5
            else:
                self.step_index += 1
        else:
            if self.current_progress < 100:
                self.current_progress += 2
            else:
                self.timer.stop()
                QTimer.singleShot(350, self.loading_finished.emit)

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()

        # 1. Conteneur arrondi avec ombre et liseré mauve
        card_rect = QRectF(10, 10, w - 20, h - 20)
        card_path = QPainterPath()
        card_path.addRoundedRect(card_rect, 16, 16)

        if self.is_light_mode:
            # Fond blanc pur avec dégradé radial doux
            bg_grad = QRadialGradient(w * 0.5, h * 0.45, w * 0.6)
            bg_grad.setColorAt(0.0, QColor(255, 255, 255))
            bg_grad.setColorAt(0.5, QColor(248, 250, 252))
            bg_grad.setColorAt(1.0, QColor(241, 245, 249))
            painter.fillPath(card_path, QBrush(bg_grad))

            # Bordure mauve néon
            border_alpha = int(180 + 50 * math.sin(self.pulse))
            pen_border = QPen(QColor(124, 58, 237, border_alpha), 2)
            painter.setPen(pen_border)
            painter.drawPath(card_path)

            # Décoration grille cybernétique discrète
            grid_pen = QPen(QColor(124, 58, 237, 12), 1)
            painter.setPen(grid_pen)
            for gx in range(20, w - 20, 40):
                painter.drawLine(gx, 20, gx, h - 20)
            for gy in range(20, h - 20, 40):
                painter.drawLine(20, gy, w - 20, gy)

        else:
            # Fond noir profond avec dégradé radial d'accent mauve
            bg_grad = QRadialGradient(w * 0.5, h * 0.45, w * 0.6)
            bg_grad.setColorAt(0.0, QColor(22, 10, 38))
            bg_grad.setColorAt(0.5, QColor(10, 9, 14))
            bg_grad.setColorAt(1.0, QColor(4, 4, 6))
            painter.fillPath(card_path, QBrush(bg_grad))

            # Bordure néon mauve pulsante
            border_alpha = int(170 + 60 * math.sin(self.pulse))
            pen_border = QPen(QColor(139, 92, 246, border_alpha), 2)
            painter.setPen(pen_border)
            painter.drawPath(card_path)

            # Décoration grille cybernétique
            grid_pen = QPen(QColor(124, 58, 237, 12), 1)
            painter.setPen(grid_pen)
            for gx in range(20, w - 20, 40):
                painter.drawLine(gx, 20, gx, h - 20)
            for gy in range(20, h - 20, 40):
                painter.drawLine(20, gy, w - 20, gy)

        # 2. Logo officiel GRAN LAKU / GLC CONVERTER
        y_cursor = 40
        if self.logo_pix:
            lx = (w - self.logo_pix.width()) // 2
            painter.drawPixmap(lx, y_cursor, self.logo_pix)
            y_cursor += self.logo_pix.height() + 14
        else:
            painter.setPen(QColor("#0f172a" if self.is_light_mode else "#ffffff"))
            painter.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
            painter.drawText(QRectF(20, y_cursor, w - 40, 34), Qt.AlignmentFlag.AlignCenter, APP_NAME)
            y_cursor += 38

        # Sous-titre officiel
        painter.setPen(QColor("#6b21a8" if self.is_light_mode else "#c084fc"))
        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        painter.drawText(QRectF(20, y_cursor, w - 40, 20), Qt.AlignmentFlag.AlignCenter,
                         f"STUDIO UNIVERSEL DE CONVERSION • {COMPANY_NAME.upper()}")
        y_cursor += 34

        # Badge Version & Définition 12K
        badge_rect = QRectF(w * 0.5 - 110, y_cursor, 220, 24)
        badge_path = QPainterPath()
        badge_path.addRoundedRect(badge_rect, 6, 6)

        if self.is_light_mode:
            painter.fillPath(badge_path, QColor(243, 232, 255, 240))
            painter.setPen(QPen(QColor(192, 132, 252, 200), 1))
            painter.drawPath(badge_path)
            painter.setPen(QColor("#581c87"))
        else:
            painter.fillPath(badge_path, QColor(36, 14, 62, 200))
            painter.setPen(QPen(QColor(168, 85, 247, 180), 1))
            painter.drawPath(badge_path)
            painter.setPen(QColor("#ffffff"))

        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        painter.drawText(badge_rect, Qt.AlignmentFlag.AlignCenter, "● 12K DCI CINEMA & GPU ACCEL")
        y_cursor += 50

        # 3. Barre de Progression Laser Futuriste
        bar_x = 45
        bar_w = w - 90
        bar_h = 8
        bar_y = y_cursor

        # Fond de la jauge
        bar_bg_rect = QRectF(bar_x, bar_y, bar_w, bar_h)
        bar_bg_path = QPainterPath()
        bar_bg_path.addRoundedRect(bar_bg_rect, 4, 4)

        if self.is_light_mode:
            painter.fillPath(bar_bg_path, QColor(226, 232, 240))
            painter.setPen(QPen(QColor(192, 132, 252, 160), 1))
        else:
            painter.fillPath(bar_bg_path, QColor(15, 12, 20))
            painter.setPen(QPen(QColor(124, 58, 237, 80), 1))
        painter.drawPath(bar_bg_path)

        # Remplissage laser néon
        pct = min(100.0, max(0.0, self.current_progress))
        fill_w = (bar_w * pct) / 100.0
        if fill_w > 0:
            fill_rect = QRectF(bar_x, bar_y, fill_w, bar_h)
            fill_path = QPainterPath()
            fill_path.addRoundedRect(fill_rect, 4, 4)

            laser_grad = QLinearGradient(bar_x, 0, bar_x + fill_w, 0)
            if self.is_light_mode:
                laser_grad.setColorAt(0.0, QColor("#581c87"))
                laser_grad.setColorAt(0.5, QColor("#7c3aed"))
                laser_grad.setColorAt(1.0, QColor("#a855f7"))
            else:
                laser_grad.setColorAt(0.0, QColor("#6b21a8"))
                laser_grad.setColorAt(0.5, QColor("#a855f7"))
                laser_grad.setColorAt(1.0, QColor("#e879f9"))
            painter.fillPath(fill_path, QBrush(laser_grad))

            # Point lumineux à la tête de la jauge
            head_glow = QRadialGradient(bar_x + fill_w, bar_y + bar_h / 2, 10)
            if self.is_light_mode:
                head_glow.setColorAt(0.0, QColor(124, 58, 237, 240))
                head_glow.setColorAt(1.0, QColor(168, 85, 247, 0))
            else:
                head_glow.setColorAt(0.0, QColor(245, 208, 254, 220))
                head_glow.setColorAt(1.0, QColor(168, 85, 247, 0))
            painter.setBrush(QBrush(head_glow))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QRectF(bar_x + fill_w - 6, bar_y - 3, 14, 14))

        # Compteur de pourcentage
        painter.setPen(QColor("#581c87" if self.is_light_mode else "#ffffff"))
        painter.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        pct_text = f"{int(pct)}%"
        painter.drawText(QRectF(w - 110, bar_y - 24, 65, 20), Qt.AlignmentFlag.AlignRight, pct_text)

        # 4. Message de Statut Holographique
        painter.setPen(QColor("#6b21a8" if self.is_light_mode else "#d8b4fe"))
        painter.setFont(QFont("Consolas", 9, QFont.Weight.Normal))
        status_rect = QRectF(bar_x, bar_y + 18, bar_w, 24)
        painter.drawText(status_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self.status_text)

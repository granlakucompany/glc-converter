"""
GLC CONVERTER — Arrière-Plan Studio Cybernétique (Thème Clair & Thème Sombre)
Éditeur: GRAN LAKU COMPANY | https://granlaku.com/glcconverter
"""
import random
import math
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor, QPen, QRadialGradient, QLinearGradient, QBrush
from PySide6.QtWidgets import QWidget

class CyberBackgroundWidget(QWidget):
    """
    Toile de fond haute technologie adaptative :
    - Thème Sombre (défaut) : Fond noir profond avec lueurs néon violettes et grille cybernétique.
    - Thème Clair : Fond blanc cassé/ardoise lumineux avec réseau de particules et liaisons mauves douces.
    """

    def __init__(self, parent=None, is_light_mode: bool = False):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, False)
        self.is_light_mode = is_light_mode

        # Génération du réseau de particules d'accent mauve
        self.num_particles = 48
        self.particles = []
        self._init_particles()

        # Ligne de balayage cybernétique mauve (Scanline)
        self.scanline_y = 0.0
        self.scanline_speed = 1.0

        # Timer d'animation fluide à ~35 FPS
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate)
        self.timer.start(28)

    def set_light_mode(self, is_light: bool):
        self.is_light_mode = is_light
        self._init_particles()
        self.update()

    def _init_particles(self):
        self.particles = []
        if self.is_light_mode:
            mauve_accents = [
                QColor(124, 58, 237),  # Mauve riche
                QColor(147, 51, 234),  # Violet vibrant
                QColor(168, 85, 247),  # Lavande
                QColor(107, 33, 168)   # Mauve profond
            ]
            alpha_range = (60, 140)
        else:
            mauve_accents = [
                QColor(168, 85, 247),  # Mauve vibrant
                QColor(139, 92, 246),  # Violet électrique
                QColor(192, 132, 252), # Lavande néon
                QColor(126, 34, 206)   # Mauve profond
            ]
            alpha_range = (150, 240)

        for _ in range(self.num_particles):
            self.particles.append({
                "x": random.uniform(0, 1920),
                "y": random.uniform(0, 1080),
                "vx": random.uniform(-0.35, 0.35),
                "vy": random.uniform(-0.25, 0.25),
                "r": random.uniform(1.6, 2.8),
                "color": random.choice(mauve_accents),
                "alpha": random.uniform(*alpha_range),
                "pulse": random.uniform(0, math.pi * 2)
            })

    def _animate(self):
        w = max(self.width(), 800)
        h = max(self.height(), 600)

        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["pulse"] += 0.04

            # Rebond sur les bords
            if p["x"] < 0: p["x"] = w
            elif p["x"] > w: p["x"] = 0
            if p["y"] < 0: p["y"] = h
            elif p["y"] > h: p["y"] = 0

        # Balayage radar vertical doux
        self.scanline_y += self.scanline_speed
        if self.scanline_y > h:
            self.scanline_y = 0

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()

        if self.is_light_mode:
            # 1. Fond Thème Clair : Dégradé Blanc / Ardoise Lumineux / Lavande
            bg_gradient = QRadialGradient(w * 0.5, h * 0.35, max(w, h) * 0.85)
            bg_gradient.setColorAt(0.0, QColor(250, 245, 255))  # Centre lavande lumineux
            bg_gradient.setColorAt(0.5, QColor(245, 247, 250))  # Ardoise clair
            bg_gradient.setColorAt(1.0, QColor(234, 240, 246))  # Bords contrastés
            painter.fillRect(self.rect(), bg_gradient)

            # 2. Grille cybernétique dynamique
            grid_pen = QPen(QColor(124, 58, 237, 22))
            grid_pen.setWidth(1)
            painter.setPen(grid_pen)
            grid_size = 60
            for x in range(0, w, grid_size):
                painter.drawLine(x, 0, x, h)
            for y in range(0, h, grid_size):
                painter.drawLine(0, y, w, y)

            major_pen = QPen(QColor(124, 58, 237, 45))
            major_pen.setWidth(1)
            painter.setPen(major_pen)
            for x in range(0, w, grid_size * 3):
                painter.drawLine(x, 0, x, h)
            for y in range(0, h, grid_size * 3):
                painter.drawLine(0, y, w, y)

            # 3. Ligne de balayage mauve
            scan_grad = QLinearGradient(0, self.scanline_y - 25, 0, self.scanline_y + 25)
            scan_grad.setColorAt(0.0, QColor(124, 58, 237, 0))
            scan_grad.setColorAt(0.5, QColor(124, 58, 237, 22))
            scan_grad.setColorAt(1.0, QColor(124, 58, 237, 0))
            painter.fillRect(0, int(self.scanline_y - 25), w, 50, QBrush(scan_grad))

            # 4. Dessin des liaisons du réseau quantique
            pen_line = QPen()
            pen_line.setWidth(1)
            max_dist = 135
            num = len(self.particles)
            for i in range(num):
                p1 = self.particles[i]
                for j in range(i + 1, num):
                    p2 = self.particles[j]
                    dx = p1["x"] - p2["x"]
                    dy = p1["y"] - p2["y"]
                    dist = math.hypot(dx, dy)
                    if dist < max_dist:
                        alpha = int((1.0 - (dist / max_dist)) * 55)
                        pen_line.setColor(QColor(124, 58, 237, alpha))
                        painter.setPen(pen_line)
                        painter.drawLine(int(p1["x"]), int(p1["y"]), int(p2["x"]), int(p2["y"]))

        else:
            # 1. Dégradé de fond : Aura Cybernétique Violette & Noir Profond
            bg_gradient = QRadialGradient(w * 0.5, h * 0.45, max(w, h) * 0.85)
            bg_gradient.setColorAt(0.0, QColor(36, 16, 64))   # Aura violette centrale
            bg_gradient.setColorAt(0.35, QColor(16, 9, 28))  # Transition douce
            bg_gradient.setColorAt(0.7, QColor(9, 7, 14))    # Noir nuit studio
            bg_gradient.setColorAt(1.0, QColor(4, 4, 6))     # Bords sombres
            painter.fillRect(self.rect(), bg_gradient)

            # 2. Grille cybernétique nettement visible
            grid_pen = QPen(QColor(139, 92, 246, 26))
            grid_pen.setWidth(1)
            painter.setPen(grid_pen)
            grid_size = 60
            for x in range(0, w, grid_size):
                painter.drawLine(x, 0, x, h)
            for y in range(0, h, grid_size):
                painter.drawLine(0, y, w, y)

            major_pen = QPen(QColor(168, 85, 247, 48))
            major_pen.setWidth(1)
            painter.setPen(major_pen)
            for x in range(0, w, grid_size * 3):
                painter.drawLine(x, 0, x, h)
            for y in range(0, h, grid_size * 3):
                painter.drawLine(0, y, w, y)

            # 3. Ligne de balayage holographique mauve
            scan_grad = QLinearGradient(0, self.scanline_y - 25, 0, self.scanline_y + 25)
            scan_grad.setColorAt(0.0, QColor(168, 85, 247, 0))
            scan_grad.setColorAt(0.5, QColor(168, 85, 247, 30))
            scan_grad.setColorAt(1.0, QColor(168, 85, 247, 0))
            painter.fillRect(0, int(self.scanline_y - 25), w, 50, QBrush(scan_grad))

            # 4. Dessin des liaisons du réseau quantique
            pen_line = QPen()
            pen_line.setWidth(1)
            max_dist = 135
            num = len(self.particles)
            for i in range(num):
                p1 = self.particles[i]
                for j in range(i + 1, num):
                    p2 = self.particles[j]
                    dx = p1["x"] - p2["x"]
                    dy = p1["y"] - p2["y"]
                    dist = math.hypot(dx, dy)
                    if dist < max_dist:
                        alpha = int((1.0 - (dist / max_dist)) * 75)
                        pen_line.setColor(QColor(147, 51, 234, alpha))
                        painter.setPen(pen_line)
                        painter.drawLine(int(p1["x"]), int(p1["y"]), int(p2["x"]), int(p2["y"]))

        # 5. Dessin des nœuds (particules d'accent mauve)
        for p in self.particles:
            pulse_factor = 0.8 + 0.3 * math.sin(p["pulse"])
            current_radius = p["r"] * pulse_factor

            c = QColor(p["color"])
            c.setAlpha(int(p["alpha"]))

            # Halo externe
            halo_grad = QRadialGradient(p["x"], p["y"], current_radius * 2.5)
            halo_c = QColor(c)
            halo_c.setAlpha(int(p["alpha"] * 0.35))
            halo_grad.setColorAt(0.0, halo_c)
            halo_grad.setColorAt(1.0, QColor(c.red(), c.green(), c.blue(), 0))
            painter.setBrush(QBrush(halo_grad))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(int(p["x"] - current_radius * 2.2), int(p["y"] - current_radius * 2.2),
                               int(current_radius * 4.4), int(current_radius * 4.4))

            # Point central lumineux
            painter.setBrush(QBrush(c))
            painter.drawEllipse(int(p["x"] - current_radius), int(p["y"] - current_radius),
                               int(current_radius * 2), int(current_radius * 2))

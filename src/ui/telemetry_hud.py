"""
GLC CONVERTER — Panneau de Télémétrie & HUD Matériel en Temps Réel (Monochrome Mauve)
Éditeur: GRAN LAKU COMPANY | https://granlaku.com/glcconverter
"""
import psutil
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QLabel, QProgressBar
)
from ..core.hw_accel import HardwareDetector

class TelemetryHUD(QFrame):
    """Bandeau d'instrumentation HUD futuriste affichant la télémétrie système en direct."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("telemetryHud")
        self.hw = HardwareDetector.get_instance()
        self._setup_ui()

        # Rafraîchissement toutes les 1.2 secondes
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._refresh_telemetry)
        self.timer.start(1200)

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 6, 14, 6)
        layout.setSpacing(16)

        # Indicateur Système Status
        self.lbl_status = QLabel("● CORE ONLINE")
        self.lbl_status.setStyleSheet("color: #c084fc; font-weight: 800; font-size: 11px; letter-spacing: 0.8px;")
        layout.addWidget(self.lbl_status)

        # Jauge CPU
        cpu_box = QHBoxLayout()
        cpu_box.setSpacing(6)
        lbl_cpu_title = QLabel("CPU:")
        lbl_cpu_title.setStyleSheet("color: #d8b4fe; font-size: 11px; font-weight: 700;")
        cpu_box.addWidget(lbl_cpu_title)

        self.cpu_bar = QProgressBar()
        self.cpu_bar.setFixedSize(70, 10)
        self.cpu_bar.setTextVisible(False)
        self.cpu_bar.setRange(0, 100)
        self.cpu_bar.setStyleSheet("""
            QProgressBar {
                background-color: rgba(22, 9, 38, 0.9);
                border: 1px solid rgba(124, 58, 237, 0.4);
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6b21a8, stop:1 #c084fc);
                border-radius: 3px;
            }
        """)
        cpu_box.addWidget(self.cpu_bar)

        self.lbl_cpu_val = QLabel("0%")
        self.lbl_cpu_val.setStyleSheet("color: #f5f3ff; font-size: 11px; font-weight: 600; min-width: 32px;")
        cpu_box.addWidget(self.lbl_cpu_val)
        layout.addLayout(cpu_box)

        # Jauge RAM
        ram_box = QHBoxLayout()
        ram_box.setSpacing(6)
        lbl_ram_title = QLabel("RAM:")
        lbl_ram_title.setStyleSheet("color: #c4b5fd; font-size: 11px; font-weight: 700;")
        ram_box.addWidget(lbl_ram_title)

        self.ram_bar = QProgressBar()
        self.ram_bar.setFixedSize(70, 10)
        self.ram_bar.setTextVisible(False)
        self.ram_bar.setRange(0, 100)
        self.ram_bar.setStyleSheet("""
            QProgressBar {
                background-color: rgba(22, 9, 38, 0.9);
                border: 1px solid rgba(124, 58, 237, 0.4);
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #581c87, stop:1 #a855f7);
                border-radius: 3px;
            }
        """)
        ram_box.addWidget(self.ram_bar)

        self.lbl_ram_val = QLabel("0%")
        self.lbl_ram_val.setStyleSheet("color: #f5f3ff; font-size: 11px; font-weight: 600; min-width: 32px;")
        ram_box.addWidget(self.lbl_ram_val)
        layout.addLayout(ram_box)

        layout.addStretch()

        # Accélération Matérielle Badge
        gpu_accel = "NVENC CUDA" if self.hw.nvenc_available else ("QUICKSYNC" if self.hw.qsv_available else ("AMF RADEON" if self.hw.amf_available else "CPU THREADS"))
        self.lbl_gpu = QLabel(f"⚡ PIPELINE: {gpu_accel} | 12K READY")
        self.lbl_gpu.setStyleSheet("""
            background: rgba(58, 20, 96, 0.7);
            border: 1px solid #a855f7;
            color: #ffffff;
            font-weight: 800;
            font-size: 11px;
            padding: 3px 10px;
            border-radius: 6px;
            letter-spacing: 0.5px;
        """)
        layout.addWidget(self.lbl_gpu)

        # Mode Moteur
        self.lbl_mode = QLabel("DÉTERMINISTE 60FPS")
        self.lbl_mode.setStyleSheet("""
            background: rgba(38, 14, 64, 0.85);
            border: 1px solid rgba(168, 85, 247, 0.5);
            color: #d8b4fe;
            font-weight: 700;
            font-size: 11px;
            padding: 3px 10px;
            border-radius: 6px;
        """)
        layout.addWidget(self.lbl_mode)

    def _refresh_telemetry(self):
        try:
            cpu_pct = int(psutil.cpu_percent())
            ram_pct = int(psutil.virtual_memory().percent)
            self.cpu_bar.setValue(cpu_pct)
            self.lbl_cpu_val.setText(f"{cpu_pct}%")
            self.ram_bar.setValue(ram_pct)
            self.lbl_ram_val.setText(f"{ram_pct}%")
        except Exception:
            pass

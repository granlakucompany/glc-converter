"""
GLC CONVERTER — Lecteur Plein Écran Haute Fidélité Studio
Éditeur: GRAN LAKU COMPANY | https://granlaku.com/glcconverter
"""
import os
import sys
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QUrl, QTimer, Signal, QEvent
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSlider, QStackedWidget, QWidget, QFrame, QSizePolicy
)
from PySide6.QtGui import QPixmap, QImage, QKeyEvent, QMouseEvent, QFont, QColor
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget

def create_web_view(parent=None):
    """Instanciation dynamique et sécurisée de QWebEngineView à la demande."""
    try:
        from PySide6.QtWebEngineWidgets import QWebEngineView
        return QWebEngineView(parent)
    except Exception:
        return None

from ..core.mime_detector import MimeDetector


class FullScreenStudioPlayer(QDialog):
    """
    Lecteur Média Plein Écran Studio Haute Technologie.
    Prend en charge les Vidéos 12K/4K/HD, les animations HTML5 interactives, l'audio et les images.
    Synchronisation dynamique de position, barre de contrôle auto-masquable et raccourcis clavier.
    """

    playback_closed = Signal(int, bool)  # (position_ms, is_playing)

    def __init__(
        self,
        filepath: str,
        start_position_ms: int = 0,
        auto_play: bool = True,
        initial_volume: int = 80,
        parent=None
    ):
        super().__init__(parent)
        if filepath.startswith("http://") or filepath.startswith("https://"):
            self.filepath = filepath
        else:
            self.filepath = str(Path(filepath).resolve())
        self.current_pos = start_position_ms
        self.initial_auto_play = auto_play
        self.initial_volume = initial_volume
        self.is_playing = False
        self.duration_ms = 0
        self.is_muted = False

        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.setMouseTracking(True)

        self._setup_ui()
        self._setup_player()
        self._load_file()

        # Timer d'auto-masquage des contrôles en plein écran (après 3s d'inactivité)
        self.hide_timer = QTimer(self)
        self.hide_timer.setInterval(3000)
        self.hide_timer.timeout.connect(self._auto_hide_controls)
        self.hide_timer.start()

    def _setup_ui(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #040407;
            }
            #topBar, #bottomBar {
                background-color: rgba(9, 9, 13, 0.88);
                border: 1px solid rgba(139, 92, 246, 0.35);
                border-radius: 10px;
                padding: 6px 14px;
            }
            QLabel {
                color: #f8fafc;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton#btnFSAction {
                background-color: #2a0f44;
                border: 1px solid #7c3aed;
                border-radius: 6px;
                color: #ffffff;
                font-size: 13px;
                font-weight: 800;
                padding: 6px 12px;
                min-width: 32px;
                min-height: 28px;
            }
            QPushButton#btnFSAction:hover {
                background-color: #6b21a8;
                border-color: #a855f7;
            }
            QPushButton#btnFSClose {
                background-color: #450a0a;
                border: 1px solid #ef4444;
                border-radius: 6px;
                color: #ffffff;
                font-size: 13px;
                font-weight: 800;
                padding: 6px 14px;
            }
            QPushButton#btnFSClose:hover {
                background-color: #991b1b;
            }
            QSlider::groove:horizontal {
                height: 6px;
                background: #1e1b4b;
                border-radius: 3px;
            }
            QSlider::sub-page:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7c3aed, stop:1 #38bdf8);
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #ffffff;
                border: 2px solid #a855f7;
                width: 14px;
                margin-top: -4px;
                margin-bottom: -4px;
                border-radius: 7px;
            }
            QSlider::handle:horizontal:hover {
                background: #c084fc;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(8)

        # 1. Barre Supérieure Flottante (Titre + Badge + Fermer)
        self.top_bar = QFrame()
        self.top_bar.setObjectName("topBar")
        top_layout = QHBoxLayout(self.top_bar)
        top_layout.setContentsMargins(10, 4, 10, 4)

        self.lbl_title = QLabel(f"◈ {Path(self.filepath).name}")
        self.lbl_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        top_layout.addWidget(self.lbl_title)

        top_layout.addStretch()

        self.lbl_badge = QLabel("STUDIO")
        self.lbl_badge.setStyleSheet("""
            background: #581c87;
            color: #d8b4fe;
            border: 1px solid #a855f7;
            border-radius: 4px;
            padding: 3px 10px;
            font-size: 11px;
            font-weight: 800;
        """)
        top_layout.addWidget(self.lbl_badge)

        self.btn_exit_fs = QPushButton("🗗 Quitter Plein Écran")
        self.btn_exit_fs.setObjectName("btnFSAction")
        self.btn_exit_fs.clicked.connect(self._close_fullscreen)
        top_layout.addWidget(self.btn_exit_fs)

        self.btn_close = QPushButton("✕")
        self.btn_close.setObjectName("btnFSClose")
        self.btn_close.setToolTip("Fermer (Échap)")
        self.btn_close.clicked.connect(self._close_fullscreen)
        top_layout.addWidget(self.btn_close)

        main_layout.addWidget(self.top_bar)

        # 2. Zone d'Affichage Centrale (QStackedWidget)
        self.stack = QStackedWidget()
        self.stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Page 0 : Image / Audio Artwork / Fallback
        self.lbl_display = QLabel()
        self.lbl_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_display.setStyleSheet("background-color: #000000; border-radius: 8px;")
        self.stack.addWidget(self.lbl_display)

        # Page 1 : Lecteur Vidéo Natif
        self.video_widget = QVideoWidget()
        self.video_widget.setStyleSheet("background-color: #000000; border-radius: 8px;")
        self.stack.addWidget(self.video_widget)

        # Page 2 : Vue Web Interactive HTML5 (chargée à la demande)
        self.web_view = None

        main_layout.addWidget(self.stack, stretch=1)

        # 3. Barre de Contrôles Inférieure Flottante
        self.bottom_bar = QFrame()
        self.bottom_bar.setObjectName("bottomBar")
        bot_layout = QHBoxLayout(self.bottom_bar)
        bot_layout.setContentsMargins(12, 6, 12, 6)
        bot_layout.setSpacing(12)

        # Bouton Play / Pause
        self.btn_play = QPushButton("▶")
        self.btn_play.setObjectName("btnFSAction")
        self.btn_play.setFixedWidth(44)
        self.btn_play.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.btn_play.clicked.connect(self._toggle_play_pause)
        bot_layout.addWidget(self.btn_play)

        # Curseur de Progression Temporelle (Timeline Scrubber)
        self.time_slider = QSlider(Qt.Orientation.Horizontal)
        self.time_slider.setRange(0, 1000)
        self.time_slider.setValue(0)
        self.time_slider.sliderMoved.connect(self._on_seek_moved)
        bot_layout.addWidget(self.time_slider, stretch=1)

        # Libellé du Temps (00:00 / 00:00)
        self.lbl_time = QLabel("00:00 / 00:00")
        self.lbl_time.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
        self.lbl_time.setFixedWidth(110)
        self.lbl_time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bot_layout.addWidget(self.lbl_time)

        # Bouton Mute
        self.btn_mute = QPushButton("🔊")
        self.btn_mute.setObjectName("btnFSAction")
        self.btn_mute.setFixedWidth(38)
        self.btn_mute.clicked.connect(self._toggle_mute)
        bot_layout.addWidget(self.btn_mute)

        # Curseur de Volume
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(self.initial_volume)
        self.volume_slider.setFixedWidth(90)
        self.volume_slider.valueChanged.connect(self._on_volume_changed)
        bot_layout.addWidget(self.volume_slider)

        main_layout.addWidget(self.bottom_bar)

    def _setup_player(self):
        self.player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.player.setAudioOutput(self.audio_output)
        self.player.setVideoOutput(self.video_widget)

        self.audio_output.setVolume(self.initial_volume / 100.0)

        self.player.positionChanged.connect(self._on_position_changed)
        self.player.durationChanged.connect(self._on_duration_changed)
        self.player.playbackStateChanged.connect(self._on_playback_state_changed)

    def _load_file(self):
        is_http_url = self.filepath.startswith("http://") or self.filepath.startswith("https://")
        if is_http_url:
            self.lbl_badge.setText("WEB STREAM / LIVE")
            if self.web_view is None:
                self.web_view = create_web_view()
                if self.web_view is not None:
                    self.web_view.setStyleSheet("background-color: #000000; border-radius: 8px;")
                    self.stack.addWidget(self.web_view)
            if self.web_view is not None:
                self.stack.setCurrentWidget(self.web_view)
                self.web_view.load(QUrl(self.filepath))
            else:
                self.stack.setCurrentIndex(0)
            self.btn_play.setText("⏸")
            self.is_playing = True
            self.duration_ms = 5000
            self.time_slider.setRange(0, self.duration_ms)
            self._update_time_label(0, self.duration_ms)
            return

        p = Path(self.filepath)
        if not p.exists():
            return

        ext = p.suffix.lower()
        info = MimeDetector.identify_file(str(p))
        cat = info.get("category", "other").lower()

        if ext in [".html", ".htm", ".xml", ".xhtml"]:
            self.lbl_badge.setText("ANIMATION XML / WEB" if ext in [".xml", ".xhtml"] else "ANIMATION HTML5")
            if self.web_view is None:
                self.web_view = create_web_view()
                if self.web_view is not None:
                    self.web_view.setStyleSheet("background-color: #000000; border-radius: 8px;")
                    self.stack.addWidget(self.web_view)
            if self.web_view is not None:
                self.stack.setCurrentWidget(self.web_view)
                self.web_view.load(QUrl.fromLocalFile(str(p)))
            else:
                self.stack.setCurrentIndex(0)
            self.btn_play.setText("⏸")
            self.is_playing = True
            # Tenter de charger l'audio associé si détecté
            from ..core.html_detector import HtmlDetector
            meta = HtmlDetector.detect_html_metadata(str(p))
            dur = meta.get("duration", 10.0)
            self.duration_ms = int(dur * 1000)
            self.time_slider.setRange(0, self.duration_ms)
            self._update_time_label(0, self.duration_ms)
            audio_p = meta.get("audio_path")
            if audio_p and os.path.exists(audio_p):
                self.player.setSource(QUrl.fromLocalFile(audio_p))
                if self.initial_auto_play:
                    self.player.play()

        elif cat == "video" or ext in [".mp4", ".mkv", ".webm", ".avi", ".mov", ".ts", ".m4v"]:
            self.lbl_badge.setText("VIDÉO ULTRA HD")
            self.stack.setCurrentIndex(1)
            self.player.setSource(QUrl.fromLocalFile(str(p)))
            if self.current_pos > 0:
                self.player.setPosition(self.current_pos)
            if self.initial_auto_play:
                self.player.play()
                self.is_playing = True
                self.btn_play.setText("⏸")
            else:
                self.btn_play.setText("▶")

        elif cat == "audio" or ext in [".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a"]:
            self.lbl_badge.setText("AUDIO MASTER")
            self.stack.setCurrentIndex(0)
            pix = QPixmap(600, 400)
            pix.fill(QColor(10, 10, 15))
            self.lbl_display.setPixmap(pix)
            self.player.setSource(QUrl.fromLocalFile(str(p)))
            if self.current_pos > 0:
                self.player.setPosition(self.current_pos)
            if self.initial_auto_play:
                self.player.play()
                self.is_playing = True
                self.btn_play.setText("⏸")
            else:
                self.btn_play.setText("▶")

        elif cat == "image":
            self.lbl_badge.setText("IMAGE SOURCE")
            self.stack.setCurrentIndex(0)
            pix = QPixmap(str(p))
            if not pix.isNull():
                self.lbl_display.setPixmap(pix.scaled(1600, 900, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            self.time_slider.setEnabled(False)
            self.btn_play.setEnabled(False)
            self.lbl_time.setText("IMAGE")

        else:
            self.lbl_badge.setText(cat.upper())
            self.stack.setCurrentIndex(0)
            self.lbl_display.setText(f"Aperçu Média : {p.name}")

    def _toggle_play_pause(self):
        if self.stack.currentIndex() == 2 and self.web_view:
            # HTML5 Animation
            self.is_playing = not self.is_playing
            self.btn_play.setText("⏸" if self.is_playing else "▶")
            cmd = "document.querySelectorAll('video, audio').forEach(el => el.paused ? el.play() : el.pause());"
            self.web_view.page().runJavaScript(cmd)
            if self.player.source().isValid():
                if self.is_playing:
                    self.player.play()
                else:
                    self.player.pause()
            return

        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
            self.is_playing = False
            self.btn_play.setText("▶")
        else:
            self.player.play()
            self.is_playing = True
            self.btn_play.setText("⏸")

    def _on_seek_moved(self, pos_ms: int):
        self.player.setPosition(pos_ms)
        self._update_time_label(pos_ms, self.duration_ms)

    def _on_position_changed(self, pos_ms: int):
        self.current_pos = pos_ms
        if not self.time_slider.isSliderDown():
            self.time_slider.setValue(pos_ms)
        self._update_time_label(pos_ms, self.duration_ms)

    def _on_duration_changed(self, dur_ms: int):
        self.duration_ms = dur_ms
        self.time_slider.setRange(0, dur_ms)
        self._update_time_label(self.current_pos, dur_ms)

    def _on_playback_state_changed(self, state):
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.is_playing = True
            self.btn_play.setText("⏸")
        else:
            self.is_playing = False
            self.btn_play.setText("▶")

    def _on_volume_changed(self, val: int):
        self.audio_output.setVolume(val / 100.0)
        if val == 0:
            self.btn_mute.setText("🔇")
            self.is_muted = True
        else:
            self.btn_mute.setText("🔊")
            self.is_muted = False
        if self.web_view:
            self.web_view.page().setAudioMuted(val == 0)

    def _toggle_mute(self):
        self.is_muted = not self.is_muted
        self.audio_output.setMuted(self.is_muted)
        self.btn_mute.setText("🔇" if self.is_muted else "🔊")
        if self.web_view:
            self.web_view.page().setAudioMuted(self.is_muted)

    def _update_time_label(self, cur_ms: int, dur_ms: int):
        c_sec = max(0, cur_ms // 1000)
        d_sec = max(0, dur_ms // 1000)
        c_min, c_sec = divmod(c_sec, 60)
        d_min, d_sec = divmod(d_sec, 60)
        self.lbl_time.setText(f"{c_min:02d}:{c_sec:02d} / {d_min:02d}:{d_sec:02d}")

    def _auto_hide_controls(self):
        if self.is_playing:
            self.top_bar.hide()
            self.bottom_bar.hide()

    def mouseMoveEvent(self, event: QMouseEvent):
        self.top_bar.show()
        self.bottom_bar.show()
        self.hide_timer.start(3000)
        super().mouseMoveEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        self._close_fullscreen()

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        if key in (Qt.Key.Key_Escape, Qt.Key.Key_F11):
            self._close_fullscreen()
        elif key == Qt.Key.Key_Space:
            self._toggle_play_pause()
        elif key == Qt.Key.Key_M:
            self._toggle_mute()
        elif key == Qt.Key.Key_Left:
            self.player.setPosition(max(0, self.player.position() - 5000))
        elif key == Qt.Key.Key_Right:
            self.player.setPosition(min(self.duration_ms, self.player.position() + 5000))
        elif key == Qt.Key.Key_Up:
            new_v = min(100, self.volume_slider.value() + 5)
            self.volume_slider.setValue(new_v)
        elif key == Qt.Key.Key_Down:
            new_v = max(0, self.volume_slider.value() - 5)
            self.volume_slider.setValue(new_v)
        else:
            super().keyPressEvent(event)

    def _close_fullscreen(self):
        final_pos = self.player.position() if self.player else self.current_pos
        was_play = self.is_playing
        if self.player:
            self.player.stop()
        self.playback_closed.emit(final_pos, was_play)
        self.close()

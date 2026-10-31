"""
GLC CONVERTER — Carte d'Aperçu Média Haute Fidélité Studio (Thème Clair & Thème Sombre)
Éditeur: GRAN LAKU COMPANY | https://granlaku.com/glcconverter
"""
import os
import subprocess
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QWidget, QGridLayout, QSlider, QStackedWidget, QSizePolicy
)
from PySide6.QtGui import QPixmap, QImage, QPainter, QColor, QFont, QMouseEvent
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget

def create_web_view(parent=None):
    """Instanciation dynamique et sécurisée de QWebEngineView à la demande."""
    try:
        from PySide6.QtWebEngineWidgets import QWebEngineView
        return QWebEngineView(parent)
    except Exception:
        return None

import av
from PIL import Image

from ..core.mime_detector import MimeDetector
from ..core.converter_engine import ConversionTask
from ..core.i18n import I18nManager, tr
from .fullscreen_player import FullScreenStudioPlayer


class MediaPreviewCard(QFrame):
    """
    Carte d'inspection multimédia de studio haute fidélité.
    Intègre un mini-lecteur dynamique pour les vidéos, animations HTML5 et pistes audio,
    avec boutons Play/Pause, contrôle de volume, scrubber temporel et mode Plein Écran synchronisé.
    """

    open_full_preview = Signal(str)
    remove_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("mediaPreviewCard")
        self.current_task: Optional[ConversionTask] = None
        self.current_filepath: Optional[str] = None
        self.duration_ms: int = 0
        self.is_muted: bool = False
        self.is_html_mode: bool = False
        self.fs_player: Optional[FullScreenStudioPlayer] = None

        self._setup_ui()
        self._setup_media_player()
        self.reset_to_empty()
        self.retranslate_ui()
        I18nManager.get_instance().register_listener(self.retranslate_ui)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(4)

        # 1. En-tête de la carte
        header_layout = QHBoxLayout()
        self.header_title = QLabel(tr("inspector_title"))
        self.header_title.setObjectName("cardHeaderTitle")
        # Hauteur fixe : sinon l'espace libre de la carte étire l'en-tête (badge géant)
        self.header_title.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        header_layout.addWidget(self.header_title)

        header_layout.addStretch()

        self.lbl_badge_category = QLabel(tr("inspector_standby"))
        self.lbl_badge_category.setObjectName("inspectorBadge")
        self.lbl_badge_category.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        header_layout.addWidget(self.lbl_badge_category)
        layout.addLayout(header_layout)

        # 2. Zone d'affichage visuel (Viewport Studio) avec lecteur intégré
        self.viewport_frame = QFrame()
        self.viewport_frame.setObjectName("inspectorViewport")
        self.viewport_frame.setMinimumHeight(80)
        self.viewport_frame.setMaximumHeight(180)
        self.viewport_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.viewport_frame.mouseDoubleClickEvent = self._on_viewport_double_clicked
        vp_layout = QVBoxLayout(self.viewport_frame)
        vp_layout.setContentsMargins(0, 0, 0, 0)
        vp_layout.setSpacing(0)

        # Pile de widgets d'affichage (Thumbnail / Video / HTML5)
        self.media_stack = QStackedWidget()
        self.media_stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Page 0 : Image / Audio Artwork / Placeholder
        self.lbl_thumbnail = QLabel()
        self.lbl_thumbnail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_thumbnail.setStyleSheet("background: transparent;")
        self.media_stack.addWidget(self.lbl_thumbnail)

        # Page 1 : Vidéo Natif Hardware QVideoWidget
        self.video_widget = QVideoWidget()
        self.video_widget.setStyleSheet("background-color: #050508; border-top-left-radius: 9px; border-top-right-radius: 9px;")
        self.media_stack.addWidget(self.video_widget)

        # Page 2 : Animation Web & Canvas HTML5
        # Créée dès maintenant (avant l'affichage de la fenêtre) : l'ajouter plus tard à une
        # fenêtre visible force Qt à détruire puis recréer la fenêtre native (effet « fermeture »).
        # Le composant de rendu interne n'apparaît qu'au premier chargement : on charge donc
        # une page vide tout de suite (web_ready passe à True quand c'est fait).
        self.web_view = create_web_view()
        self.web_ready = self.web_view is None
        if self.web_view is not None:
            try:
                self.web_view.page().setBackgroundColor(QColor("#050508"))
            except Exception:
                pass
            self.web_view.setStyleSheet("background-color: #050508; border-top-left-radius: 9px; border-top-right-radius: 9px;")
            self.media_stack.addWidget(self.web_view)
            self.web_view.loadFinished.connect(self._on_web_view_warmed)
            self.web_view.setHtml("<html><body style='margin:0;background:#050508'></body></html>")

        vp_layout.addWidget(self.media_stack, stretch=1)

        # Barre de Contrôles Média Intégrée (Play, Timeline, Volume, Plein Écran)
        self.controls_bar = QFrame()
        self.controls_bar.setObjectName("playerControlBar")
        ctrl_layout = QHBoxLayout(self.controls_bar)
        ctrl_layout.setContentsMargins(4, 2, 4, 2)
        ctrl_layout.setSpacing(4)

        # Bouton Play / Pause
        self.btn_play = QPushButton("▶")
        self.btn_play.setObjectName("btnPlayerCtrl")
        self.btn_play.setFixedSize(26, 26)
        self.btn_play.setToolTip("Lecture / Pause")
        self.btn_play.clicked.connect(self._toggle_play_pause)
        ctrl_layout.addWidget(self.btn_play)

        # Scrubber Temporel (Barre de Progression)
        self.time_slider = QSlider(Qt.Orientation.Horizontal)
        self.time_slider.setObjectName("playerTimeSlider")
        self.time_slider.setRange(0, 1000)
        self.time_slider.setValue(0)
        self.time_slider.sliderMoved.connect(self._on_seek_moved)
        ctrl_layout.addWidget(self.time_slider, stretch=1)

        # Horodatage
        # Format compact « 00:00/00:30 » : largeur calculée sur le texte réel (l'ancienne
        # largeur fixe de 56 px coupait « 00:00 / 00:00 »)
        self.lbl_time = QLabel("00:00/00:00")
        self.lbl_time.setObjectName("playerTimeLabel")
        self.lbl_time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_time.setStyleSheet("font-size: 10px; font-weight: 700; font-family: Consolas, monospace;")
        self.lbl_time.ensurePolished()
        self.lbl_time.setFixedWidth(self.lbl_time.fontMetrics().horizontalAdvance("00:00/00:00") + 8)
        ctrl_layout.addWidget(self.lbl_time)

        # Bouton Muet / Volume
        self.btn_mute = QPushButton("🔊")
        self.btn_mute.setObjectName("btnPlayerCtrl")
        self.btn_mute.setFixedSize(24, 24)
        self.btn_mute.setToolTip("Activer / Couper le son")
        self.btn_mute.clicked.connect(self._toggle_mute)
        ctrl_layout.addWidget(self.btn_mute)

        # Curseur de Volume
        self.vol_slider = QSlider(Qt.Orientation.Horizontal)
        self.vol_slider.setObjectName("playerVolSlider")
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(80)
        self.vol_slider.setFixedWidth(36)
        self.vol_slider.setToolTip("Volume sonore")
        self.vol_slider.valueChanged.connect(self._on_volume_changed)
        ctrl_layout.addWidget(self.vol_slider)

        # Bouton Plein Écran (Full Screen)
        self.btn_fullscreen = QPushButton("⛶")
        self.btn_fullscreen.setObjectName("btnPlayerFS")
        self.btn_fullscreen.setFixedSize(26, 26)
        self.btn_fullscreen.setToolTip("Ouvrir en Plein Écran (Double-clic ou Échap pour quitter)")
        self.btn_fullscreen.clicked.connect(self._open_fullscreen_player)
        ctrl_layout.addWidget(self.btn_fullscreen)

        vp_layout.addWidget(self.controls_bar)
        layout.addWidget(self.viewport_frame)

        # 3. Nom du fichier
        self.lbl_filename = QLabel(tr("no_media_selected"))
        self.lbl_filename.setObjectName("inspectorFilename")
        self.lbl_filename.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_filename.setFixedHeight(20)
        layout.addWidget(self.lbl_filename)

        # 4. Grille de Métadonnées Dynamiques
        self.meta_grid = QGridLayout()
        self.meta_grid.setSpacing(2)
        self.meta_grid.setContentsMargins(0, 0, 0, 0)

        # Résolution (Ligne 0, Col 0)
        self.lbl_res_label = QLabel(tr("meta_resolution"))
        self.lbl_res_label.setObjectName("metaLabel")
        self.lbl_res_val = QLabel("--")
        self.lbl_res_val.setObjectName("metaVal")
        self.meta_grid.addWidget(self.lbl_res_label, 0, 0)
        self.meta_grid.addWidget(self.lbl_res_val, 1, 0)

        # Codec / Format (Ligne 0, Col 1)
        self.lbl_codec_label = QLabel(tr("meta_codec"))
        self.lbl_codec_label.setObjectName("metaLabel")
        self.lbl_codec_val = QLabel("--")
        self.lbl_codec_val.setObjectName("metaVal")
        self.meta_grid.addWidget(self.lbl_codec_label, 0, 1)
        self.meta_grid.addWidget(self.lbl_codec_val, 1, 1)

        # Durée / Cadence (Ligne 2, Col 0)
        self.lbl_time_label = QLabel(tr("meta_framerate"))
        self.lbl_time_label.setObjectName("metaLabel")
        self.lbl_time_val = QLabel("--")
        self.lbl_time_val.setObjectName("metaVal")
        self.meta_grid.addWidget(self.lbl_time_label, 2, 0)
        self.meta_grid.addWidget(self.lbl_time_val, 3, 0)

        # Poids disque (Ligne 2, Col 1)
        self.lbl_size_label = QLabel(tr("meta_bitrate"))
        self.lbl_size_label.setObjectName("metaLabel")
        self.lbl_size_val = QLabel("--")
        self.lbl_size_val.setObjectName("metaVal")
        self.meta_grid.addWidget(self.lbl_size_label, 2, 1)
        self.meta_grid.addWidget(self.lbl_size_val, 3, 1)

        self.meta_grid.setColumnStretch(0, 1)
        self.meta_grid.setColumnStretch(1, 1)

        layout.addLayout(self.meta_grid)
        layout.addStretch(1)

        # 5. Boutons d'Action Rapide de la Carte
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(6)
        self.btn_inspect = QPushButton("🔍 Aperçu")
        self.btn_inspect.setObjectName("btnInspect")
        self.btn_inspect.clicked.connect(self._open_fullscreen_player)
        btn_layout.addWidget(self.btn_inspect)

        self.btn_open_folder = QPushButton("📁 Dossier")
        self.btn_open_folder.setObjectName("btnOpenFolder")
        self.btn_open_folder.clicked.connect(self._on_open_folder_clicked)
        btn_layout.addWidget(self.btn_open_folder)

        layout.addLayout(btn_layout)

    def _on_web_view_warmed(self, _ok: bool):
        self.web_ready = True

    def _setup_media_player(self):
        self.player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.player.setAudioOutput(self.audio_output)
        self.player.setVideoOutput(self.video_widget)

        self.audio_output.setVolume(self.vol_slider.value() / 100.0)

        self.player.positionChanged.connect(self._on_player_position_changed)
        self.player.durationChanged.connect(self._on_player_duration_changed)
        self.player.playbackStateChanged.connect(self._on_playback_state_changed)

    def retranslate_ui(self, lang_code: str = None):
        """Met à jour les libellés de l'inspecteur avec concision et élégance."""
        clean_title = tr("inspector_title").replace("STUDIO MEDIA INSPECTOR", "INSPECTEUR").replace("INSPECTOR", "INSPECTEUR")
        self.header_title.setText(clean_title)
        if self.current_filepath is None:
            self.lbl_badge_category.setText(tr("inspector_standby"))
            self.lbl_filename.setText(tr("no_media_selected"))
        
        cur_lang = (lang_code or getattr(I18nManager.get_instance(), "current_lang", "fr")).lower()
        if "ht" in cur_lang:
            self.lbl_res_label.setText("Rezolisyon")
            self.lbl_codec_label.setText("Kodek")
            self.lbl_time_label.setText("Kadans")
            self.lbl_size_label.setText("Pwa")
            self.btn_inspect.setText("🔍 Apèsi")
            self.btn_open_folder.setText("📁 Dosye")
        elif "en" in cur_lang:
            self.lbl_res_label.setText("Resolution")
            self.lbl_codec_label.setText("Codec")
            self.lbl_time_label.setText("Framerate")
            self.lbl_size_label.setText("Size")
            self.btn_inspect.setText("🔍 Preview")
            self.btn_open_folder.setText("📁 Folder")
        elif "es" in cur_lang:
            self.lbl_res_label.setText("Resolución")
            self.lbl_codec_label.setText("Códec")
            self.lbl_time_label.setText("Cuadros")
            self.lbl_size_label.setText("Tamaño")
            self.btn_inspect.setText("🔍 Vista previa")
            self.btn_open_folder.setText("📁 Carpeta")
        else:
            self.lbl_res_label.setText("Résolution")
            self.lbl_codec_label.setText("Codec")
            self.lbl_time_label.setText("Cadence")
            self.lbl_size_label.setText("Poids")
            self.btn_inspect.setText("🔍 Aperçu")
            self.btn_open_folder.setText("📁 Dossier")

    def reset_to_empty(self):
        """Réinitialise la carte et le lecteur à son état d'attente."""
        self.current_filepath = None
        self.is_html_mode = False
        self.lbl_badge_category.setText(tr("inspector_standby"))

        if self.player:
            self.player.stop()
            self.player.setSource(QUrl())

        self.media_stack.setCurrentIndex(0)

        # Placeholder visuel stylisé
        # Une seule ligne, 48 px de haut : à 960×600 la zone d'aperçu ne fait
        # qu'environ 60 px et l'ancienne image 320×160 sur deux lignes était coupée.
        placeholder_pix = QPixmap(260, 48)
        placeholder_pix.fill(QColor(0, 0, 0, 0))
        painter = QPainter(placeholder_pix)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QColor(124, 58, 237, 140))
        painter.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        painter.drawText(placeholder_pix.rect(), Qt.AlignmentFlag.AlignCenter, "◈  MEDIA READY")
        painter.end()
        self.lbl_thumbnail.setPixmap(placeholder_pix)

        self.lbl_filename.setText(tr("no_media_selected"))
        self.lbl_res_val.setText("--")
        self.lbl_codec_val.setText("--")
        self.lbl_time_val.setText("--")
        self.lbl_size_val.setText("--")

        self.time_slider.setValue(0)
        self.time_slider.setEnabled(False)
        self.btn_play.setText("▶")
        self.btn_play.setEnabled(False)
        self.btn_fullscreen.setEnabled(False)
        self.lbl_time.setText("00:00/00:00")
        self.btn_inspect.setEnabled(False)
        self.btn_open_folder.setEnabled(False)

    def inspect_task(self, task: ConversionTask):
        """Charge et analyse une tâche de conversion."""
        self.current_task = task
        self.current_filepath = task.input_path
        self.load_media(task.input_path)

    def load_media(self, filepath: str):
        """Extrait la miniature, les métadonnées et prépare le lecteur multimédia."""
        s_fp = str(filepath).strip()
        is_http_url = s_fp.startswith("http://") or s_fp.startswith("https://")

        if not is_http_url:
            path = Path(filepath)
            if not path.exists():
                return
            self.current_filepath = str(path)
            self.lbl_filename.setText(path.name)
            ext = path.suffix.lower().lstrip(".")
            size_mb = path.stat().st_size / (1024 * 1024)
            self.lbl_size_val.setText(f"{size_mb:.1f} Mo")
        else:
            path = None
            self.current_filepath = s_fp
            from urllib.parse import urlparse
            p_url = urlparse(s_fp)
            display_name = (p_url.netloc + (p_url.path if p_url.path not in ["", "/"] else "")) or s_fp
            self.lbl_filename.setText(display_name)
            ext = "html"
            self.lbl_size_val.setText("URL Web")

        self.btn_inspect.setEnabled(True)
        self.btn_open_folder.setEnabled(not is_http_url)
        self.btn_fullscreen.setEnabled(True)

        info = MimeDetector.identify_file(self.current_filepath)
        cat = info.get("category", "other").upper()
        self.lbl_badge_category.setText(cat)
        self.lbl_codec_val.setText("URL / WEB" if is_http_url else ext.upper())

        # Chargement selon la catégorie
        if cat in ["IMAGE"] and path:
            self.is_html_mode = False
            self._load_image_meta(path)
        elif cat in ["VIDEO"] and path:
            self.is_html_mode = False
            self._load_video_meta(path)
        elif cat in ["AUDIO"] and path:
            self.is_html_mode = False
            self._load_audio_meta(path)
        elif cat in ["WEB"] or ext in ["html", "htm", "xml", "xhtml"] or is_http_url:
            self.is_html_mode = True
            if is_http_url:
                self._load_web_url_meta(s_fp)
            else:
                self._load_web_meta(path)
        else:
            self.is_html_mode = False
            if path:
                self._load_generic_meta(path, cat)

    def _load_web_url_meta(self, url: str):
        """Charge une URL web ou un serveur local dans le lecteur interactif."""
        self.lbl_res_val.setText("1920x1080")
        self.lbl_codec_val.setText("WEB / LIVE")
        self.lbl_time_val.setText("Interactif (Web)")
        self.duration_ms = 5000
        self.time_slider.setRange(0, self.duration_ms)
        self._update_time_label(0, self.duration_ms)
        self.player.setSource(QUrl())

        if self.web_view is not None:
            self.media_stack.setCurrentWidget(self.web_view)
            try:
                self.web_view.setZoomFactor(0.3)
            except Exception:
                pass
            self.web_view.load(QUrl(url))
        else:
            self.media_stack.setCurrentIndex(0)
            self._load_fallback_pixmap("🌐")

        self.btn_play.setEnabled(True)
        self.btn_play.setText("⏸")
        self.time_slider.setEnabled(True)

    def _load_web_meta(self, path: Path):
        """Charge une animation HTML5 dans le lecteur interactif."""
        try:
            from ..core.html_detector import HtmlDetector
            meta = HtmlDetector.detect_html_metadata(str(path))
            w = meta.get("width", 1920)
            h = meta.get("height", 1080)
            dur = meta.get("duration", 5.0)
            fps = meta.get("fps", 30)
            audio = meta.get("audio_path")

            self.lbl_res_val.setText(f"{w}x{h}")
            self.lbl_codec_val.setText("HTML5 / KADANS" if audio else "HTML5 / ANIM")
            audio_info = f" (+ Audio: {Path(audio).stem[:12]})" if audio else ""
            self.lbl_time_val.setText(f"{dur:.1f}s ({fps} fps){audio_info}")

            self.duration_ms = int(dur * 1000)
            self.time_slider.setRange(0, self.duration_ms)
            self._update_time_label(0, self.duration_ms)

            # Charger l'audio associé s'il existe
            if audio and os.path.exists(audio):
                self.player.setSource(QUrl.fromLocalFile(audio))
            else:
                self.player.setSource(QUrl())

        except Exception:
            self.lbl_res_val.setText("--")
            self.lbl_time_val.setText("--")

        if self.web_view is not None:
            self.media_stack.setCurrentWidget(self.web_view)
            try:
                zoom = min(320.0 / max(w, 1), 160.0 / max(h, 1))
                if zoom > 0:
                    self.web_view.setZoomFactor(zoom)
            except Exception:
                pass
            self.web_view.load(QUrl.fromLocalFile(str(path.resolve())))
        else:
            self.media_stack.setCurrentIndex(0)
            self._load_fallback_pixmap("🌐")

        self.btn_play.setEnabled(True)
        self.btn_play.setText("⏸")
        self.time_slider.setEnabled(True)

    def _load_image_meta(self, path: Path):
        """Charge une image fixe."""
        try:
            with Image.open(path) as img:
                w, h = img.size
                fmt = img.format or path.suffix.upper()
                self.lbl_res_val.setText(f"{w}x{h}")
                self.lbl_codec_val.setText(fmt)
                self.lbl_time_val.setText(f"{img.mode}")

                img.thumbnail((320, 160))
                qimg = self._pil_to_qimage(img)
                self.lbl_thumbnail.setPixmap(QPixmap.fromImage(qimg))
        except Exception:
            self._load_fallback_pixmap("🖼️")

        self.media_stack.setCurrentIndex(0)
        self.btn_play.setEnabled(False)
        self.time_slider.setEnabled(False)
        self.lbl_time.setText("IMAGE")

    def _load_video_meta(self, path: Path):
        """Charge une vidéo dans le lecteur vidéo natif hardware."""
        try:
            container = av.open(str(path))
            v_stream = next((s for s in container.streams if s.type == "video"), None)
            if v_stream:
                w = v_stream.width
                h = v_stream.height
                codec = v_stream.codec_context.name.upper()
                fps = float(v_stream.average_rate) if v_stream.average_rate else 0.0

                duration_sec = float(container.duration / av.time_base) if container.duration else 0.0
                m, s = divmod(int(duration_sec), 60)
                time_str = f"{m:02d}:{s:02d} ({fps:.0f} fps)"

                self.lbl_res_val.setText(f"{w}x{h}")
                self.lbl_codec_val.setText(codec)
                self.lbl_time_val.setText(time_str)

                # Extraire une frame initiale
                for frame in container.decode(v_stream):
                    pil_img = frame.to_image()
                    pil_img.thumbnail((320, 160))
                    self.lbl_thumbnail.setPixmap(QPixmap.fromImage(self._pil_to_qimage(pil_img)))
                    break
            container.close()
        except Exception:
            self._load_fallback_pixmap("🎬")

        self.media_stack.setCurrentIndex(1)
        self.player.setSource(QUrl.fromLocalFile(str(path.resolve())))
        self.btn_play.setEnabled(True)
        self.btn_play.setText("▶")
        self.time_slider.setEnabled(True)

    def _load_audio_meta(self, path: Path):
        """Charge une piste audio."""
        try:
            container = av.open(str(path))
            a_stream = next((s for s in container.streams if s.type == "audio"), None)
            if a_stream:
                rate = a_stream.rate
                channels = a_stream.channels
                codec = a_stream.codec_context.name.upper()

                duration_sec = float(container.duration / av.time_base) if container.duration else 0.0
                m, s = divmod(int(duration_sec), 60)

                self.lbl_res_val.setText(f"{rate} Hz")
                self.lbl_codec_val.setText(codec)
                self.lbl_time_val.setText(f"{m:02d}:{s:02d} ({channels}ch)")
            container.close()
        except Exception:
            self.lbl_res_val.setText("--")
            self.lbl_time_val.setText("--")

        self._load_fallback_pixmap("🎵")
        self.media_stack.setCurrentIndex(0)
        self.player.setSource(QUrl.fromLocalFile(str(path.resolve())))
        self.btn_play.setEnabled(True)
        self.btn_play.setText("▶")
        self.time_slider.setEnabled(True)

    def _load_generic_meta(self, path: Path, cat: str):
        icon = "📄" if cat == "DOCUMENT" else "🧊" if cat == "3D" else "📁"
        self._load_fallback_pixmap(icon)
        self.lbl_res_val.setText("--")
        self.lbl_time_val.setText("--")
        self.media_stack.setCurrentIndex(0)
        self.btn_play.setEnabled(False)
        self.time_slider.setEnabled(False)

    def _load_fallback_pixmap(self, icon: str):
        pix = QPixmap(320, 160)
        pix.fill(QColor(0, 0, 0, 0))
        p = QPainter(pix)
        p.setPen(QColor(124, 58, 237))
        p.setFont(QFont("Segoe UI", 44))
        p.drawText(pix.rect(), Qt.AlignmentFlag.AlignCenter, icon)
        p.end()
        self.lbl_thumbnail.setPixmap(pix)

    def _pil_to_qimage(self, pil_img: Image.Image) -> QImage:
        if pil_img.mode != "RGBA":
            pil_img = pil_img.convert("RGBA")
        data = pil_img.tobytes("raw", "RGBA")
        return QImage(data, pil_img.width, pil_img.height, QImage.Format.Format_RGBA8888)

    # =========================================================================
    # CONTRÔLES DE LECTURE & ÉVÉNEMENTS DU LECTEUR
    # =========================================================================

    def _toggle_play_pause(self):
        if self.is_html_mode and self.web_view is not None:
            cmd = "document.querySelectorAll('video, audio').forEach(el => el.paused ? el.play() : el.pause());"
            self.web_view.page().runJavaScript(cmd)
            if self.player.source().isValid():
                if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
                    self.player.pause()
                    self.btn_play.setText("▶")
                else:
                    self.player.play()
                    self.btn_play.setText("⏸")
            else:
                current_text = self.btn_play.text()
                self.btn_play.setText("▶" if current_text == "⏸" else "⏸")
            return

        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
            self.btn_play.setText("▶")
        else:
            self.player.play()
            self.btn_play.setText("⏸")

    def _on_seek_moved(self, pos_ms: int):
        self.player.setPosition(pos_ms)
        self._update_time_label(pos_ms, self.duration_ms)

    def _on_player_position_changed(self, pos_ms: int):
        if not self.time_slider.isSliderDown():
            self.time_slider.setValue(pos_ms)
        self._update_time_label(pos_ms, self.duration_ms)

    def _on_player_duration_changed(self, dur_ms: int):
        self.duration_ms = dur_ms
        self.time_slider.setRange(0, dur_ms)
        self._update_time_label(self.player.position(), dur_ms)

    def _on_playback_state_changed(self, state):
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.btn_play.setText("⏸")
        else:
            self.btn_play.setText("▶")

    def _on_volume_changed(self, val: int):
        self.audio_output.setVolume(val / 100.0)
        if val == 0:
            self.btn_mute.setText("🔇")
            self.is_muted = True
        else:
            self.btn_mute.setText("🔊")
            self.is_muted = False
        if self.is_html_mode and self.web_view:
            self.web_view.page().setAudioMuted(val == 0)

    def _toggle_mute(self):
        self.is_muted = not self.is_muted
        self.audio_output.setMuted(self.is_muted)
        self.btn_mute.setText("🔇" if self.is_muted else "🔊")
        if self.is_html_mode and self.web_view:
            self.web_view.page().setAudioMuted(self.is_muted)

    def _update_time_label(self, cur_ms: int, dur_ms: int):
        c_sec = max(0, cur_ms // 1000)
        d_sec = max(0, dur_ms // 1000)
        c_min, c_sec = divmod(c_sec, 60)
        d_min, d_sec = divmod(d_sec, 60)
        self.lbl_time.setText(f"{c_min:02d}:{c_sec:02d}/{d_min:02d}:{d_sec:02d}")

    def _on_viewport_double_clicked(self, event: QMouseEvent):
        if self.current_filepath:
            is_url = self.current_filepath.startswith("http://") or self.current_filepath.startswith("https://")
            if is_url or Path(self.current_filepath).exists():
                self._open_fullscreen_player()

    def _open_fullscreen_player(self):
        """Ouvre le lecteur haute fidélité en plein écran avec synchronisation temps-réel."""
        if not self.current_filepath:
            return
        is_url = self.current_filepath.startswith("http://") or self.current_filepath.startswith("https://")
        if not is_url and not Path(self.current_filepath).exists():
            return

        cur_pos = self.player.position() if self.player else 0
        was_playing = (self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState) if self.player else False

        if self.player:
            self.player.pause()

        self.fs_player = FullScreenStudioPlayer(
            filepath=self.current_filepath,
            start_position_ms=cur_pos,
            auto_play=was_playing or True,
            initial_volume=self.vol_slider.value(),
            parent=self.window()
        )
        self.fs_player.playback_closed.connect(self._on_fullscreen_closed)
        self.fs_player.showFullScreen()

    def _on_fullscreen_closed(self, final_pos: int, was_playing: bool):
        """Reprend la lecture synchronisée dans la carte miniature dès la sortie du plein écran."""
        if self.player and self.current_filepath:
            self.player.setPosition(final_pos)
            if was_playing:
                self.player.play()
                self.btn_play.setText("⏸")
            else:
                self.player.pause()
                self.btn_play.setText("▶")

    def _on_open_folder_clicked(self):
        if self.current_filepath and Path(self.current_filepath).exists():
            subprocess.Popen(f'explorer /select,"{os.path.abspath(self.current_filepath)}"')

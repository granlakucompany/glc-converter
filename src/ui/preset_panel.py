"""
GLC CONVERTER — Étape 2 : Sélecteur de Formats Didactique & Accessible
Éditeur: GRAN LAKU COMPANY | https://granlaku.com/glcconverter
"""
import time

from PySide6.QtCore import Qt, Signal, QPoint, QEvent
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QSpinBox, QCheckBox, QWidget, QPushButton, QButtonGroup,
    QStackedWidget, QGridLayout, QSizePolicy
)
from ..core.hw_accel import HardwareDetector
from ..core.i18n import I18nManager, tr

_QUALITY_HINTS = {
    "fr": "12 = meilleure · 35 = plus léger",
    "ht": "12 = pi bon · 35 = pi lejè",
    "en": "12 = best · 35 = smallest",
    "es": "12 = mejor · 35 = más ligero",
    "pt": "12 = melhor · 35 = mais leve",
    "de": "12 = beste · 35 = kleinste",
    "it": "12 = migliore · 35 = più leggero",
    "zh": "12 = 最佳 · 35 = 最小",
    "ru": "12 = лучшее · 35 = меньше",
}


def _current_lang() -> str:
    code = (getattr(I18nManager.get_instance(), "current_lang", "fr") or "fr").lower()
    return code[:2]


class _AdvancedPopup(QFrame):
    """Panneau flottant des réglages avancés (se ferme au clic à l'extérieur)."""

    closed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def hideEvent(self, event):
        super().hideEvent(event)
        self.closed.emit()


class _ElidingButton(QPushButton):
    """Bouton dont le libellé se termine par « … » quand la carte est trop étroite.
    Le suffixe (flèche ▼/▲) reste toujours visible et le texte complet passe en infobulle.
    Les traductions longues (« Réglages Avancés & 12K DCI (Optionnel) ») débordaient de la carte."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._label = ""
        self._suffix = ""
        policy = self.sizePolicy()
        policy.setHorizontalPolicy(QSizePolicy.Policy.Ignored)
        self.setSizePolicy(policy)

    def set_label(self, label: str, suffix: str = ""):
        self._label = label
        self._suffix = suffix
        self._refresh()

    def full_text(self) -> str:
        return f"{self._label}{self._suffix}"

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._refresh()

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() in (QEvent.Type.FontChange, QEvent.Type.StyleChange):
            self._refresh()

    def _refresh(self):
        fm = self.fontMetrics()
        full = self.full_text()
        available = max(0, self.width() - 4)
        if fm.horizontalAdvance(full) <= available:
            shown = full
        else:
            label_width = max(0, available - fm.horizontalAdvance(self._suffix))
            shown = fm.elidedText(self._label, Qt.TextElideMode.ElideRight, label_width) + self._suffix
        self.setToolTip(full if shown != full else "")
        # « & » est un raccourci clavier pour Qt : il faut le doubler pour l'afficher
        super().setText(shown.replace("&", "&&"))


class PresetPanel(QFrame):
    """
    Panneau didactique de sélection du format cible (Étape 2 du workflow).
    Offre un choix instantané par catégorie avec divulgation progressive des options expertes (12K).
    """

    preset_changed = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("presetPanel")
        self._setup_ui()
        self.retranslate_ui()
        I18nManager.get_instance().register_listener(self.retranslate_ui)
        # Positionnement par défaut garanti sur Vidéo (MP4 Universel)
        self.reset_to_default()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(6)

        # 1. Badge d'Étape Didactique
        self.lbl_step = QLabel(tr("step2_title"))
        self.lbl_step.setObjectName("stepBadge")
        self.lbl_step.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_step)

        # 2. Boutons de Catégories Visuels en Grille Responsive 2x3
        cat_grid = QGridLayout()
        cat_grid.setContentsMargins(0, 0, 0, 0)
        cat_grid.setSpacing(3)
        self.btn_group = QButtonGroup(self)
        self.btn_group.setExclusive(True)

        self.cat_buttons = []
        self.cat_info = [
            ("cat_video", "video", 0, 0),
            ("cat_image", "image", 0, 1),
            ("cat_audio", "audio", 0, 2),
            ("cat_doc", "document", 1, 0),
            ("cat_web", "web", 1, 1),
            ("cat_3d", "3d", 1, 2)
        ]

        for idx, (trans_key, cat_id, r, c) in enumerate(self.cat_info):
            btn = QPushButton(tr(trans_key))
            btn.setObjectName("catButton")
            btn.setFixedHeight(28)
            btn.setCheckable(True)
            btn.setProperty("cat_id", cat_id)
            btn.setProperty("trans_key", trans_key)
            btn.clicked.connect(lambda checked, i=idx: self._on_category_button_clicked(i))
            self.btn_group.addButton(btn, idx)
            cat_grid.addWidget(btn, r, c)
            self.cat_buttons.append(btn)

        layout.addLayout(cat_grid)

        # 3. Stacked Widget pour les formats par catégorie
        self.stack = QStackedWidget()

        # Page 0: Vidéo
        p_video = QWidget()
        l_video = QHBoxLayout(p_video)
        l_video.setContentsMargins(0, 4, 0, 4)
        self.lbl_video_fmt = QLabel(tr("format_label"))
        l_video.addWidget(self.lbl_video_fmt)
        self.cb_video_fmt = QComboBox()
        self.cb_video_fmt.addItems([
            "MP4 (Universel H.264 / AAC)",
            "MKV (Haute Fidélité 8K / 12K)",
            "WebM (Optimisé Web VP9)",
            "MOV (Apple QuickTime)",
            "ProRes 422 HQ (Master Cinéma 12K)",
            "ProRes 4444 (Master avec Alpha)",
            "AVI (Standard Compatible)",
            "TS (Broadcast MPEG-TS)",
            "MXF (Master Professionnel)"
        ])
        l_video.addWidget(self.cb_video_fmt, stretch=1)
        self.stack.addWidget(p_video)

        # Page 1: Image
        p_image = QWidget()
        l_image = QHBoxLayout(p_image)
        l_image.setContentsMargins(0, 4, 0, 4)
        self.lbl_image_fmt = QLabel(tr("format_label"))
        l_image.addWidget(self.lbl_image_fmt)
        self.cb_image_fmt = QComboBox()
        self.cb_image_fmt.addItems([
            "WebP (Optimisé Web jusqu'en 12K)",
            "PNG (Transparence Lossless)",
            "JPEG (Photographie Haute Qualité)",
            "AVIF (Next-Gen Compression)",
            "TIFF (Master Archivage 12K)",
            "BMP (Bitmap Non Compressé)",
            "ICO (Icône Windows)"
        ])
        l_image.addWidget(self.cb_image_fmt, stretch=1)
        self.stack.addWidget(p_image)

        # Page 2: Audio
        p_audio = QWidget()
        l_audio = QHBoxLayout(p_audio)
        l_audio.setContentsMargins(0, 4, 0, 4)
        self.lbl_audio_fmt = QLabel(tr("format_label"))
        l_audio.addWidget(self.lbl_audio_fmt)
        self.cb_audio_fmt = QComboBox()
        self.cb_audio_fmt.addItems([
            "MP3 (Universel 320 kbps)",
            "FLAC (Audiophile Lossless 24-bit)",
            "WAV (PCM Studio 48kHz)",
            "AAC (Haute Clarté Apple)",
            "Opus (Web & Voix Ultra-Faible Latence)",
            "OGG (Ogg Vorbis Libre)"
        ])
        l_audio.addWidget(self.cb_audio_fmt, stretch=1)
        self.stack.addWidget(p_audio)

        # Page 3: Document
        p_doc = QWidget()
        l_doc = QHBoxLayout(p_doc)
        l_doc.setContentsMargins(0, 4, 0, 4)
        self.lbl_doc_fmt = QLabel(tr("format_label"))
        l_doc.addWidget(self.lbl_doc_fmt)
        self.cb_doc_fmt = QComboBox()
        self.cb_doc_fmt.addItems([
            "PDF (Document Portable Universel)",
            "Images PNG (Rendu page par page)",
            "Images WebP 12K (Rendu Haute Résolution)",
            "Texte Brut (.txt)",
            "DOCX vers PDF Haute Fidélité"
        ])
        l_doc.addWidget(self.cb_doc_fmt, stretch=1)
        self.stack.addWidget(p_doc)

        # Page 4: Web/Anim
        p_web = QWidget()
        l_web = QHBoxLayout(p_web)
        l_web.setContentsMargins(0, 4, 0, 4)
        self.lbl_web_fmt = QLabel(tr("target_label"))
        l_web.addWidget(self.lbl_web_fmt)
        self.cb_web_fmt = QComboBox()
        self.cb_web_fmt.addItems([
            "MP4 60 fps Déterministe (H.264)",
            "WebM 60 fps (VP9 avec Alpha)",
            "ProRes 422 HQ (Master Animation)"
        ])
        l_web.addWidget(self.cb_web_fmt, stretch=1)
        self.stack.addWidget(p_web)

        # Page 5: 3D
        p_3d = QWidget()
        l_3d = QHBoxLayout(p_3d)
        l_3d.setContentsMargins(0, 4, 0, 4)
        self.lbl_3d_fmt = QLabel(tr("action_label"))
        l_3d.addWidget(self.lbl_3d_fmt)
        self.cb_3d_fmt = QComboBox()
        self.cb_3d_fmt.addItems([
            "Vidéo 360° MP4 (Rotation Studio)",
            "Vidéo 360° WebM (Boucle Transparente)",
            "Convertir vers STL (Impression 3D)",
            "Convertir vers OBJ (Maillage Universel)"
        ])
        l_3d.addWidget(self.cb_3d_fmt, stretch=1)
        self.stack.addWidget(p_3d)

        layout.addWidget(self.stack)

        # 4. Réglages Avancés & 12K DCI : panneau flottant ouvert sous le bouton.
        # La carte de l'Étape 2 a une hauteur limitée : un volet déplié à l'intérieur
        # écrasait tous ses contrôles. Le panneau flottant ne prend aucune place dans la carte.
        self.btn_toggle_adv = _ElidingButton()
        self.btn_toggle_adv.setObjectName("btnAdvToggle")
        self.btn_toggle_adv.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle_adv.clicked.connect(self._toggle_advanced_options)
        layout.addWidget(self.btn_toggle_adv)

        self.adv_popup = _AdvancedPopup(self)
        self.adv_popup.closed.connect(self._on_advanced_popup_closed)
        self._adv_closed_at = 0.0
        popup_layout = QVBoxLayout(self.adv_popup)
        popup_layout.setContentsMargins(0, 0, 0, 0)

        self.adv_container = QFrame()
        self.adv_container.setObjectName("advPopup")
        popup_layout.addWidget(self.adv_container)
        l_adv = QVBoxLayout(self.adv_container)
        l_adv.setContentsMargins(14, 12, 14, 14)
        l_adv.setSpacing(8)

        self.lbl_adv_title = QLabel()
        self.lbl_adv_title.setObjectName("advPopupTitle")
        l_adv.addWidget(self.lbl_adv_title)

        self.lbl_res = QLabel(tr("resolution_label"))
        self.lbl_res.setObjectName("advPopupLabel")
        l_adv.addWidget(self.lbl_res)
        self.cb_resolution = QComboBox()
        self.cb_resolution.addItems([
            "Originale (Source)",
            "12K DCI Cinema (12288x6480)",
            "12K UHD Widescreen (11520x6480)",
            "8K UHD (7680x4320)",
            "4K UHD (3840x2160)",
            "1920x1080 (Full HD)",
            "1280x720 (HD)",
            "1080x1920 (Reels / TikTok 9:16)"
        ])
        self.cb_resolution.setMinimumHeight(32)
        l_adv.addWidget(self.cb_resolution)

        row_quality = QHBoxLayout()
        row_quality.setSpacing(8)
        self.lbl_quality = QLabel(tr("quality_label"))
        self.lbl_quality.setObjectName("advPopupLabel")
        row_quality.addWidget(self.lbl_quality)
        self.sp_crf = QSpinBox()
        self.sp_crf.setRange(12, 35)
        self.sp_crf.setValue(18)  # Qualité Master Studio par défaut (CRF 18)
        self.sp_crf.setMinimumHeight(32)
        self.sp_crf.setMinimumWidth(80)
        row_quality.addWidget(self.sp_crf)
        self.lbl_quality_hint = QLabel()
        self.lbl_quality_hint.setObjectName("advPopupHint")
        row_quality.addWidget(self.lbl_quality_hint, stretch=1)
        l_adv.addLayout(row_quality)

        self.chk_hw_accel = QCheckBox(tr("hw_accel"))
        self.chk_hw_accel.setObjectName("advPopupCheck")
        self.chk_hw_accel.setChecked(True)
        l_adv.addWidget(self.chk_hw_accel)

        # Connexions de mise à jour instantanée des contrôles de format et options
        self.cb_video_fmt.currentIndexChanged.connect(self._on_option_control_changed)
        self.cb_image_fmt.currentIndexChanged.connect(self._on_option_control_changed)
        self.cb_audio_fmt.currentIndexChanged.connect(self._on_option_control_changed)
        self.cb_doc_fmt.currentIndexChanged.connect(self._on_option_control_changed)
        self.cb_web_fmt.currentIndexChanged.connect(self._on_option_control_changed)
        self.cb_3d_fmt.currentIndexChanged.connect(self._on_option_control_changed)
        self.cb_resolution.currentIndexChanged.connect(self._on_option_control_changed)
        self.sp_crf.valueChanged.connect(self._on_option_control_changed)
        self.chk_hw_accel.toggled.connect(self._on_option_control_changed)

        # Sélectionner la catégorie Vidéo par défaut
        self.cat_buttons[0].setChecked(True)

    def retranslate_ui(self, lang_code: str = None):
        """Met à jour instantanément tous les textes dans la langue active."""
        self.lbl_step.setText(tr("step2_title"))
        for btn in self.cat_buttons:
            k = btn.property("trans_key")
            if k:
                btn.setText(tr(k))
        self.lbl_video_fmt.setText(tr("format_label"))
        self.lbl_image_fmt.setText(tr("format_label"))
        self.lbl_audio_fmt.setText(tr("format_label"))
        self.lbl_doc_fmt.setText(tr("format_label"))
        self.lbl_web_fmt.setText(tr("target_label"))
        self.lbl_3d_fmt.setText(tr("action_label"))
        self._update_adv_button_text()
        # « & » est un raccourci clavier pour Qt : il faut le doubler pour l'afficher
        self.lbl_adv_title.setText(tr("advanced_toggle"))
        self.lbl_res.setText(tr("resolution_label"))
        self.lbl_quality.setText(tr("quality_label"))
        self.lbl_quality_hint.setText(_QUALITY_HINTS.get(_current_lang(), _QUALITY_HINTS["fr"]))
        self.chk_hw_accel.setText(tr("hw_accel").replace("&", "&&"))

    def _update_adv_button_text(self):
        arrow = "▲" if self.adv_popup.isVisible() else "▼"
        self.btn_toggle_adv.set_label(tr("advanced_toggle"), f" {arrow}")

    def _on_category_button_clicked(self, idx: int):
        self.stack.setCurrentIndex(idx)
        self.preset_changed.emit(self.get_current_options())

    def _toggle_advanced_options(self):
        if self.adv_popup.isVisible():
            self.adv_popup.hide()
            return
        # Un clic sur le bouton pendant que le panneau est ouvert le ferme d'abord
        # (clic extérieur au popup) : ne pas le rouvrir aussitôt.
        if time.monotonic() - self._adv_closed_at < 0.25:
            return
        self._show_advanced_popup()

    def _show_advanced_popup(self):
        btn = self.btn_toggle_adv
        self.adv_popup.setFixedWidth(max(btn.width(), 380))
        self.adv_popup.adjustSize()
        pos = btn.mapToGlobal(QPoint(0, btn.height() + 4))

        screen = QGuiApplication.screenAt(pos) or QGuiApplication.primaryScreen()
        if screen is not None:
            area = screen.availableGeometry()
            size = self.adv_popup.sizeHint().expandedTo(self.adv_popup.size())
            x = min(max(pos.x(), area.left()), area.right() - size.width())
            y = pos.y()
            if y + size.height() > area.bottom():
                y = btn.mapToGlobal(QPoint(0, 0)).y() - size.height() - 4
            pos = QPoint(x, y)

        self.adv_popup.move(pos)
        self.adv_popup.show()
        self._update_adv_button_text()

    def _on_advanced_popup_closed(self):
        self._adv_closed_at = time.monotonic()
        self._update_adv_button_text()

    def _on_option_control_changed(self, *args):
        """Déclenché lorsqu'un format cible ou une option avancée change."""
        self.preset_changed.emit(self.get_current_options())

    def set_category(self, category: str, emit_signal: bool = True):
        """Sélectionne visuellement le bouton de la catégorie détectée."""
        cat_map = {"video": 0, "image": 1, "audio": 2, "document": 3, "web": 4, "3d": 5}
        idx = cat_map.get(category.lower(), 0)
        if 0 <= idx < len(self.cat_buttons):
            self.cat_buttons[idx].setChecked(True)
            self.stack.setCurrentIndex(idx)
            if emit_signal:
                self.preset_changed.emit(self.get_current_options())

    def reset_to_default(self):
        """Réinitialise l'Étape 2 sur sa valeur par défaut absolue : Vidéo (MP4 H.264 / AAC)."""
        self.set_category("video", emit_signal=False)
        self.cb_video_fmt.setCurrentIndex(0)
        self.cb_resolution.setCurrentIndex(0)
        self.sp_crf.setValue(18)
        self.chk_hw_accel.setChecked(True)
        self.preset_changed.emit(self.get_current_options())

    def get_options_for_category(self, category: str) -> dict:
        """Retourne les paramètres de sortie propres à une catégorie."""
        res_str = self.cb_resolution.currentText()
        resolution = None
        for pattern in ["12288x6480", "11520x6480", "7680x4320", "3840x2160", "1920x1080", "1280x720", "1080x1920"]:
            if pattern in res_str:
                resolution = pattern
                break

        opts = {
            "hw_accel": self.chk_hw_accel.isChecked(),
            "crf": self.sp_crf.value(),
            "resolution": resolution
        }

        cat = category.lower()
        if cat == "video":
            txt = self.cb_video_fmt.currentText()
            fmt = "mp4"
            if "MKV" in txt: fmt = "mkv"
            elif "WebM" in txt: fmt = "webm"
            elif "MOV" in txt: fmt = "mov"
            elif "ProRes" in txt: fmt = "mov"
            elif "AVI" in txt: fmt = "avi"
            elif "TS" in txt: fmt = "ts"
            elif "MXF" in txt: fmt = "mxf"
            opts["target_category"] = "video"
            opts["output_format"] = fmt
            opts["video_codec"] = "prores" if "ProRes" in txt else "h264"

        elif cat == "image":
            txt = self.cb_image_fmt.currentText()
            fmt = "webp"
            if "PNG" in txt: fmt = "png"
            elif "JPEG" in txt: fmt = "jpg"
            elif "AVIF" in txt: fmt = "avif"
            elif "TIFF" in txt: fmt = "tiff"
            elif "BMP" in txt: fmt = "bmp"
            elif "ICO" in txt: fmt = "ico"
            opts["target_category"] = "image"
            opts["output_format"] = fmt
            opts["quality"] = 92

        elif cat == "audio":
            txt = self.cb_audio_fmt.currentText()
            fmt = "mp3"
            if "FLAC" in txt: fmt = "flac"
            elif "WAV" in txt: fmt = "wav"
            elif "AAC" in txt: fmt = "aac"
            elif "Opus" in txt: fmt = "opus"
            elif "OGG" in txt: fmt = "ogg"
            opts["target_category"] = "audio"
            opts["output_format"] = fmt
            opts["bitrate"] = "320k"

        elif cat == "document":
            txt = self.cb_doc_fmt.currentText()
            opts["target_category"] = "document"
            if "PNG" in txt: opts["output_format"] = "png"
            elif "WebP" in txt: opts["output_format"] = "webp"
            elif "Texte" in txt: opts["output_format"] = "txt"
            else: opts["output_format"] = "pdf"

        elif cat == "web":
            txt = self.cb_web_fmt.currentText()
            opts["target_category"] = "video"
            opts["output_format"] = "webm" if "WebM" in txt else "mp4"
            opts["duration"] = 5.0

        elif cat == "3d":
            txt = self.cb_3d_fmt.currentText()
            opts["target_category"] = "3d"
            if "WebM" in txt: opts["output_format"] = "webm"
            elif "STL" in txt: opts["output_format"] = "stl"
            elif "OBJ" in txt: opts["output_format"] = "obj"
            else: opts["output_format"] = "mp4"

        else:
            opts["target_category"] = "video"
            opts["output_format"] = "mp4"

        return opts

    def get_current_options(self) -> dict:
        """Retourne les options correspondant à la catégorie actuellement active."""
        idx = self.stack.currentIndex()
        cat_map = {0: "video", 1: "image", 2: "audio", 3: "document", 4: "web", 5: "3d"}
        cat = cat_map.get(idx, "video")
        return self.get_options_for_category(cat)

    @property
    def tabs(self):
        """Propriété de rétrocompatibilité pour les anciens appels."""
        class _ProxyTabs:
            def __init__(self, stack):
                self._stack = stack
            def currentIndex(self):
                return self._stack.currentIndex()
            def setCurrentIndex(self, i):
                self._stack.setCurrentIndex(i)
        return _ProxyTabs(self.stack)

"""
GLC CONVERTER — Fenêtre Principale Studio Didactique (Workflow 3 Étapes Guidé)
Éditeur: GRAN LAKU COMPANY | https://granlaku.com/glcconverter
"""
import os
import uuid
import psutil
import subprocess
from pathlib import Path
from typing import List, Optional

from PySide6.QtCore import Qt, QThread, Signal, QTimer, QUrl
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QStatusBar, QMessageBox, QFrame,
    QSplitter, QSizePolicy, QComboBox
)
from PySide6.QtGui import QIcon, QPixmap, QDesktopServices

from ..config import (
    APP_NAME, APP_SUBTITLE, APP_VERSION, COMPANY_NAME,
    COMPANY_WEBSITE, GITHUB_URL, LOGO_PATH, LOGO_FULL_PATH, LOGO_FULL_LIGHT_PATH,
    LOGO_FULL_DARK_PATH, ICON_PATH, OUTPUT_DIR
)
from ..core.converter_engine import (
    ConverterEngine, ConversionTask, clear_allocated_output_paths,
    generate_unique_glc_output_path
)
from ..core.hw_accel import HardwareDetector
from ..core.mime_detector import MimeDetector
from ..core.i18n import I18nManager, tr, LANGUAGES
from ..core.settings_manager import get_output_dir, set_output_dir, set_last_open_dir
from .cyber_background import CyberBackgroundWidget
from .media_preview_card import MediaPreviewCard
from .drop_zone import DropZoneWidget
from .task_table import TaskTableWidget
from .preset_panel import PresetPanel
from .html_to_video_dialog import HtmlToVideoDialog
from .preview_dialog import PreviewDialog
from .about_dialog import AboutDialog
from .process_bar import ProcessProgressBar

class ConversionWorker(QThread):
    """Thread d'arrière-plan exécutant les conversions sans bloquer l'UI."""
    task_progress = Signal(ConversionTask)
    task_finished = Signal(ConversionTask)
    all_finished = Signal()

    def __init__(self, engine: ConverterEngine, tasks: List[ConversionTask]):
        super().__init__()
        self.engine = engine
        self.tasks = tasks
        self.is_paused = False
        self.is_stopped = False

    def run(self):
        for task in self.tasks:
            if self.is_stopped:
                break
            if task.status in ["Terminé", "Annulé"]:
                continue
            
            self.engine.process_task(
                task,
                on_progress=lambda t: self.task_progress.emit(t),
                on_finish=lambda t: self.task_finished.emit(t)
            )
            self.task_finished.emit(task)

        self.all_finished.emit()

    def stop(self):
        self.is_stopped = True
        for t in self.tasks:
            if t.status == "En cours":
                t.cancel()


class MainWindow(QMainWindow):
    """
    Fenêtre Principale Studio Haute Technologie didactique.
    Organisée selon un workflow universel en 3 étapes guidées claires :
    [ ① Importer ] → [ ② Choisir le Format ] → [ ③ Lancer la Conversion ]
    Supporte nativement le Thème Sombre (par défaut, reposant) et le Thème Clair.
    """

    def __init__(self, is_light_mode: bool = False):
        super().__init__()
        self.is_light_mode = is_light_mode
        self.engine = ConverterEngine()
        self.tasks: List[ConversionTask] = []
        self.worker: Optional[ConversionWorker] = None
        self.output_directory = get_output_dir()
        self.hw = HardwareDetector.get_instance()

        self.setWindowTitle(f"{APP_NAME} — {APP_SUBTITLE} ({COMPANY_NAME})")
        self.resize(1300, 860)
        self.setMinimumSize(960, 600)

        if ICON_PATH.exists():
            self.setWindowIcon(QIcon(str(ICON_PATH)))

        self._setup_ui()
        self.retranslate_ui()
        I18nManager.get_instance().register_listener(self.retranslate_ui)

        # Timer pour la télémétrie discrète dans la barre d'état
        self.telemetry_timer = QTimer(self)
        self.telemetry_timer.timeout.connect(self._update_status_bar)
        self.telemetry_timer.start(1500)
        self._update_status_bar()

    def _setup_ui(self):
        # Arrière-plan animé adaptatif (Thème Clair / Sombre)
        self.cyber_bg = CyberBackgroundWidget(is_light_mode=self.is_light_mode)
        self.setCentralWidget(self.cyber_bg)

        main_layout = QVBoxLayout(self.cyber_bg)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. En-tête Studio épuré
        main_layout.addWidget(self._create_header())

        # 2. Corps de l'application
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(14, 6, 14, 6)
        content_layout.setSpacing(6)

        # 3. LE GUIDE DIDACTIQUE EN 3 ÉTAPES (Rangée supérieure responsive)
        workflow_frame = QFrame()
        workflow_frame.setObjectName("workflowFrame")
        workflow_frame.setMinimumHeight(148)
        workflow_frame.setMaximumHeight(170)
        workflow_frame.setStyleSheet("""
            QFrame#workflowFrame {
                background: transparent;
                border: none;
            }
        """)
        workflow_layout = QHBoxLayout(workflow_frame)
        workflow_layout.setContentsMargins(0, 0, 0, 0)
        workflow_layout.setSpacing(10)

        # Étape 1 : Zone d'Importation
        self.drop_zone = DropZoneWidget()
        self.drop_zone.files_dropped.connect(self._on_files_added)
        workflow_layout.addWidget(self.drop_zone, stretch=1)

        # Étape 2 : Sélecteur de Formats (Positionné par défaut sur Vidéo)
        self.preset_panel = PresetPanel()
        self.preset_panel.preset_changed.connect(self._on_preset_changed)
        workflow_layout.addWidget(self.preset_panel, stretch=1)

        # Étape 3 : Action de Conversion & Destination
        step3_card = self._create_step3_card()
        workflow_layout.addWidget(step3_card, stretch=1)

        content_layout.addWidget(workflow_frame, stretch=0)

        # 4. Zone Inférieure : Splitter File d'Attente & Inspecteur Média
        self.bottom_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.bottom_splitter.setStyleSheet("QSplitter::handle { background-color: rgba(124, 58, 237, 0.2); width: 4px; }")

        # Tableau des tâches interactif
        self.task_table = TaskTableWidget(is_light_mode=self.is_light_mode)
        self.task_table.task_remove_requested.connect(self._remove_task)
        self.task_table.task_convert_single.connect(self._convert_single_task)
        self.task_table.preview_requested.connect(self._preview_file)
        self.task_table.itemSelectionChanged.connect(self._on_table_selection_changed)
        self.task_table.setMinimumWidth(450)
        self.bottom_splitter.addWidget(self.task_table)

        # Carte d'Inspection Média Studio
        self.preview_card = MediaPreviewCard()
        self.preview_card.open_full_preview.connect(self._preview_file)
        self.preview_card.setMinimumWidth(240)
        self.preview_card.setMaximumWidth(400)
        self.bottom_splitter.addWidget(self.preview_card)

        self.bottom_splitter.setCollapsible(0, False)
        self.bottom_splitter.setCollapsible(1, False)
        self.bottom_splitter.setStretchFactor(0, 7)
        self.bottom_splitter.setStretchFactor(1, 3)
        self.bottom_splitter.setSizes([680, 280])
        content_layout.addWidget(self.bottom_splitter, stretch=1)

        # 5. Barre de Processus Futuriste Mauve & Bleu (Process Progress Bar)
        self.process_bar = ProcessProgressBar(is_light_mode=self.is_light_mode)
        content_layout.addWidget(self.process_bar, stretch=0)

        main_layout.addWidget(content_widget)

        # 6. Barre d'état élégante avec télémétrie discrète et dernière version
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Badge permanent affichant la dernière version dans le bas (bottom / footer)
        self.btn_version_badge = QPushButton(f"🏷️ v{APP_VERSION}")
        self.btn_version_badge.setObjectName("versionBadge")
        self.btn_version_badge.setToolTip(f"{APP_NAME} — {APP_SUBTITLE}\nVersion : {APP_VERSION}\nÉditeur : {COMPANY_NAME}\nCliquez pour afficher les informations détaillées")
        self.btn_version_badge.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_version_badge.clicked.connect(self._open_about)
        self.status_bar.addPermanentWidget(self.btn_version_badge)

    def _create_header(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("headerFrame")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(14, 6, 14, 6)
        layout.setSpacing(10)

        # 1. Bloc Marque Officielle : Logo 3D Haute Résolution + Titre Net + Description Lumineuse
        brand_box = QHBoxLayout()
        brand_box.setSpacing(14)
        brand_box.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # Emblème officiel 3D haute résolution (54x54)
        self.lbl_logo_emblem = QLabel()
        self.lbl_logo_emblem.setObjectName("headerLogoEmblem")
        brand_box.addWidget(self.lbl_logo_emblem)

        # Textes typographiques vectoriels : Titre & Description (aucun flou bitmap)
        brand_text_box = QVBoxLayout()
        brand_text_box.setSpacing(2)
        brand_text_box.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        title_badge_row = QHBoxLayout()
        title_badge_row.setSpacing(10)
        title_badge_row.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self.lbl_brand_title = QLabel()
        self.lbl_brand_title.setObjectName("headerBrandTitle")
        title_badge_row.addWidget(self.lbl_brand_title)

        self.lbl_studio_badge = QLabel("PRO STUDIO")
        self.lbl_studio_badge.setObjectName("headerStudioBadge")
        title_badge_row.addWidget(self.lbl_studio_badge)
        brand_text_box.addLayout(title_badge_row)

        self.lbl_brand_desc = QLabel()
        self.lbl_brand_desc.setObjectName("headerBrandDesc")
        brand_text_box.addWidget(self.lbl_brand_desc)

        brand_box.addLayout(brand_text_box)
        layout.addLayout(brand_box)

        self._update_header_logo()

        layout.addStretch()

        # Bouton Bascule Thème Clair / Thème Sombre
        self.btn_theme_toggle = QPushButton("🌙 Sombre" if self.is_light_mode else "☀️ Clair")
        self.btn_theme_toggle.setObjectName("btnThemeToggle")
        self.btn_theme_toggle.setToolTip("Basculer entre le Thème Clair et le Thème Sombre")
        self.btn_theme_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_theme_toggle.clicked.connect(self._toggle_theme)
        layout.addWidget(self.btn_theme_toggle)

        # Sélecteur de Langue (8 langues officielles de WASDEV + Russe)
        self.cb_lang = QComboBox()
        self.cb_lang.setObjectName("cbLang")
        self.cb_lang.setToolTip(tr("lang_selector"))
        self.cb_lang.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cb_lang.setStyleSheet("""
            QComboBox#cbLang {
                padding: 4px 6px;
                font-weight: 700;
                font-size: 11px;
                border-radius: 6px;
                min-width: 115px;
            }
        """)
        lang_list = [
            ("fr", "🇫🇷 Français"),
            ("ht", "🇭🇹 Kreyòl Ayisyen"),
            ("en", "🇺🇸 English"),
            ("es", "🇪🇸 Español"),
            ("pt", "🇧🇷 Português"),
            ("de", "🇩🇪 Deutsch"),
            ("it", "🇮🇹 Italiano"),
            ("zh", "🇨🇳 简体中文"),
            ("ru", "🇷🇺 Русский"),
        ]
        current_l = I18nManager.get_instance().get_language()
        cur_idx = 0
        for i, (l_code, l_label) in enumerate(lang_list):
            self.cb_lang.addItem(l_label, l_code)
            if l_code == current_l:
                cur_idx = i
        self.cb_lang.setCurrentIndex(cur_idx)
        self.cb_lang.currentIndexChanged.connect(self._on_language_combo_changed)
        layout.addWidget(self.cb_lang)

        # Dépôt open source GitHub
        self.btn_github = QPushButton(tr("github_btn"))
        self.btn_github.setObjectName("btnGithub")
        self.btn_github.setToolTip(tr("github_tooltip"))
        self.btn_github.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_github.setStyleSheet("""
            QPushButton#btnGithub {
                background: #24292f;
                color: #ffffff;
                font-weight: 800;
                font-size: 11px;
                border: 1px solid #57606a;
                border-radius: 6px;
                padding: 5px 10px;
            }
            QPushButton#btnGithub:hover {
                background: #32383f;
            }
        """)
        self.btn_github.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(GITHUB_URL)))
        layout.addWidget(self.btn_github)

        # Bouton Officiel GRAN LAKU COMPANY
        self.btn_web = QPushButton(tr("website_btn"))
        self.btn_web.setObjectName("btnGranLaku")
        self.btn_web.setToolTip("Ouvrir le site officiel dans le navigateur")
        self.btn_web.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_web.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(COMPANY_WEBSITE)))
        layout.addWidget(self.btn_web)

        # Bouton À Propos
        self.btn_about = QPushButton(tr("about"))
        self.btn_about.clicked.connect(self._open_about)
        layout.addWidget(self.btn_about)

        return frame

    def _on_language_combo_changed(self, index: int):
        code = self.cb_lang.itemData(index)
        if code:
            I18nManager.get_instance().set_language(code)

    def _create_step3_card(self) -> QFrame:
        """Crée la carte d'action finale didactique (Étape 3 du workflow)."""
        card = QFrame()
        card.setObjectName("cardFrame")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(6)

        # Badge d'Étape Didactique
        self.lbl_step3 = QLabel(tr("step3_title"))
        self.lbl_step3.setObjectName("stepBadge")
        self.lbl_step3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_step3)

        # Dossier de destination
        dest_box = QHBoxLayout()
        self.lbl_dest_info = QLabel(f"📁 {Path(self.output_directory).name}")
        self.lbl_dest_info.setObjectName("destLabel")
        self.lbl_dest_info.setToolTip(self.output_directory)
        dest_box.addWidget(self.lbl_dest_info, stretch=1)

        self.btn_chg_dest = QPushButton(tr("change_dest"))
        self.btn_chg_dest.clicked.connect(self._change_output_directory)
        dest_box.addWidget(self.btn_chg_dest)
        layout.addLayout(dest_box)

        # Grand Bouton Primaire Immanquable
        self.btn_start = QPushButton(tr("btn_convert_all"))
        self.btn_start.setObjectName("btnPrimary")
        self.btn_start.setMinimumHeight(36)
        self.btn_start.setMaximumHeight(40)
        self.btn_start.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.btn_start.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_start.clicked.connect(self._start_conversion)
        layout.addWidget(self.btn_start)

        # Boutons d'Action Secondaires
        btn_box = QHBoxLayout()
        btn_box.setSpacing(6)

        self.btn_clear = QPushButton("🗑️ Vider")
        self.btn_clear.setObjectName("btnDanger")
        self.btn_clear.setToolTip(tr("btn_clear_tooltip"))
        self.btn_clear.clicked.connect(self._clear_tasks)
        # Le style btnDanger n'a pas de padding (prévu pour la croix du tableau) :
        # sans hauteur fixe, « Vider » était moitié moins haut que « HTML ».
        self.btn_clear.setFixedHeight(34)
        btn_box.addWidget(self.btn_clear)

        self.btn_html = QPushButton("⚡ HTML")
        self.btn_html.setFixedHeight(34)
        self.btn_html.setToolTip(tr("btn_html_tooltip"))
        self.btn_html.clicked.connect(self._open_html_converter)
        btn_box.addWidget(self.btn_html)

        layout.addLayout(btn_box)

        return card

    def _on_files_added(self, filepaths: List[str]):
        if filepaths:
            set_last_open_dir(filepaths[0])

        # L'Étape 2 (Partie 2) est positionnée par défaut sur Vidéo (MP4 Universel)
        # On utilise le format actuellement actif dans le sélecteur
        active_opts = self.preset_panel.get_current_options()
        active_fmt = active_opts.get("output_format", "mp4")

        for fp in filepaths:
            file_info = MimeDetector.identify_file(fp)
            src_cat = file_info.get("category", "other")
            opts = dict(active_opts)
            target_fmt = active_fmt

            # Détection automatique spécifique pour les composants HTML / XML / animations / URLs web
            is_url = str(fp).startswith("http://") or str(fp).startswith("https://")
            ext = "" if is_url else Path(fp).suffix.lower()
            if src_cat == "web" or ext in [".html", ".htm", ".xml", ".xhtml"] or is_url:
                try:
                    from ..core.html_detector import HtmlDetector
                    detected = HtmlDetector.detect_html_metadata(fp)
                    opts["duration"] = detected.get("duration", 5.0)
                    opts["fps"] = detected.get("fps", 30)
                    opts["width"] = detected.get("width", 1920)
                    opts["height"] = detected.get("height", 1080)
                    if detected.get("audio_path"):
                        opts["audio_path"] = detected["audio_path"]
                    file_info["resolution"] = f"{opts['width']}x{opts['height']}"
                    file_info["duration"] = f"{opts['duration']:.1f}s"
                except Exception:
                    pass

            task_id = str(uuid.uuid4())[:8]
            task = ConversionTask(
                task_id=task_id,
                input_path=fp,
                output_format=target_fmt,
                output_dir=self.output_directory,
                options=opts,
                file_info=file_info
            )
            self.tasks.append(task)
            self.task_table.add_task(task)

        # La Partie 2 (Étape 2) reste par défaut sur Vidéo
        if not any(b.isChecked() for b in self.preset_panel.cat_buttons):
            self.preset_panel.set_category("video", emit_signal=False)

        self._update_status_bar()
        if self.tasks:
            self.preview_card.inspect_task(self.tasks[-1])

    def _on_preset_changed(self, opts: dict):
        """Met à jour instantanément le format cible et les options des tâches en attente."""
        target_fmt = opts.get("output_format", "mp4").lower().lstrip(".")
        if not self.tasks:
            return

        selected_ids = set(self.task_table.get_checked_task_ids())
        for task in self.tasks:
            if task.status in ["En attente", "Erreur"]:
                if not selected_ids or task.task_id in selected_ids:
                    task.release()
                    task.output_format = target_fmt
                    task.options.update(opts)
                    new_path, unique_code = generate_unique_glc_output_path(
                        output_dir=task.output_dir,
                        input_path=task.input_path,
                        output_format=target_fmt
                    )
                    task.output_path = new_path
                    task.unique_code = unique_code

                    row = self.task_table.tasks_map.get(task.task_id)
                    if row is not None:
                        item_fmt = self.task_table.item(row, 3)
                        if item_fmt:
                            item_fmt.setText(f"➜ {target_fmt.upper()}")
                            item_fmt.setToolTip(
                                f"Format cible : {target_fmt.upper()}\nCode unique : {unique_code}\nFichier généré : {Path(new_path).name}"
                            )
                        item_name = self.task_table.item(row, 1)
                        if item_name:
                            raw_name = task.file_info.get("name") or Path(task.input_path).name or task.input_path
                            item_name.setToolTip(
                                f"Source : {task.input_path}\nFichier de sortie : {Path(new_path).name}\nCode unique GLC : {unique_code}"
                            )

    def _on_table_selection_changed(self):
        selected_rows = self.task_table.selectionModel().selectedRows()
        if selected_rows:
            row_idx = selected_rows[0].row()
            item = self.task_table.item(row_idx, 1)
            tid = item.data(Qt.ItemDataRole.UserRole) if item else None
            task = next((t for t in self.tasks if t.task_id == tid), None)
            if task:
                self.preview_card.inspect_task(task)
            elif 0 <= row_idx < len(self.tasks):
                self.preview_card.inspect_task(self.tasks[row_idx])

    def _open_html_converter(self):
        dlg = HtmlToVideoDialog(self)
        if dlg.exec():
            cfg = dlg.get_config()
            src = cfg.get("url") or cfg.get("source_path")
            is_web_url = src and (src.startswith("http://") or src.startswith("https://"))
            if not src or (not is_web_url and not Path(src).exists()):
                QMessageBox.warning(self, "Erreur", "Veuillez spécifier un fichier HTML ou une URL valide.")
                return

            task_id = str(uuid.uuid4())[:8]
            file_info = MimeDetector.identify_file(src)
            dur = cfg.get("duration", 5.0)
            w = cfg.get("width", 1920)
            h = cfg.get("height", 1080)
            file_info["resolution"] = f"{w}x{h}"
            file_info["duration"] = f"{dur:.1f}s"

            task_opts = {
                "duration": dur,
                "fps": cfg.get("fps", 30),
                "width": w,
                "height": h
            }
            if cfg.get("audio_path"):
                task_opts["audio_path"] = cfg.get("audio_path")

            task = ConversionTask(
                task_id=task_id,
                input_path=src,
                output_format=cfg.get("format", "mp4"),
                output_dir=self.output_directory,
                options=task_opts,
                file_info=file_info
            )
            self.tasks.append(task)
            self.task_table.add_task(task)
            self.preview_card.load_media(src)
            self._update_status_bar()

    def _start_conversion(self):
        if not self.tasks:
            QMessageBox.information(self, tr("msg_info"), tr("msg_add_files_first"))
            return

        checked_ids = set(self.task_table.get_checked_task_ids())
        if not checked_ids:
            QMessageBox.information(
                self, 
                tr("msg_info"), 
                tr("msg_select_at_least_one")
            )
            return

        pending_tasks = [t for t in self.tasks if t.task_id in checked_ids and t.status in ["En attente", "Erreur"]]
        if not pending_tasks:
            QMessageBox.information(self, tr("msg_info"), tr("msg_all_already_done"))
            return

        self._batch_tasks = pending_tasks
        self._completed_in_batch = 0

        self.btn_start.setEnabled(False)
        self.btn_start.setText(tr("btn_converting"))
        self.process_bar.start_process(len(pending_tasks), pending_tasks[0].input_path)

        self.worker = ConversionWorker(self.engine, pending_tasks)
        self.worker.task_progress.connect(self._on_worker_progress)
        self.worker.task_finished.connect(self._on_task_finished)
        self.worker.all_finished.connect(self._on_all_finished)
        self.worker.start()

    def _on_worker_progress(self, task: ConversionTask):
        self.task_table.update_task_progress(task)
        batch = getattr(self, "_batch_tasks", [])
        try:
            curr_idx = batch.index(task) + 1
        except (ValueError, AttributeError):
            curr_idx = 1
        total = max(1, len(batch)) if batch else 1
        self.process_bar.update_task_progress(task, curr_idx, total)

    def _on_task_finished(self, task: ConversionTask):
        self.task_table.update_task_progress(task)
        if Path(task.output_path).exists():
            self.preview_card.load_media(task.output_path)

        batch = getattr(self, "_batch_tasks", [])
        total = max(1, len(batch)) if batch else 1
        self._completed_in_batch = getattr(self, "_completed_in_batch", 0) + 1
        self.process_bar.on_task_completed(task, self._completed_in_batch, total)
        self._update_status_bar()

    def _on_all_finished(self):
        self.btn_start.setEnabled(True)
        self.btn_start.setText(tr("btn_convert_all"))
        self.process_bar.finish_process(success=True)
        self._update_status_bar()
        QMessageBox.information(self, tr("msg_success"), tr("msg_all_finished_success"))

    def _convert_single_task(self, task_id: str):
        """Lance la conversion individuelle d'un fichier spécifique depuis sa ligne."""
        target_task = None
        for t in self.tasks:
            if t.task_id == task_id:
                target_task = t
                break
        if not target_task:
            return
        if target_task.status == "En cours":
            return

        target_task.status = "En attente"
        target_task.progress = 0
        self.task_table.update_task_progress(target_task)

        self._batch_tasks = [target_task]
        self._completed_in_batch = 0
        self.process_bar.start_process(1, target_task.input_path)

        single_worker = ConversionWorker(self.engine, [target_task])
        single_worker.task_progress.connect(self._on_worker_progress)
        single_worker.task_finished.connect(self._on_task_finished)
        single_worker.all_finished.connect(lambda: self.process_bar.finish_process(success=True))
        single_worker.start()

        if not hasattr(self, "_single_workers"):
            self._single_workers = []
        self._single_workers.append(single_worker)
        single_worker.finished.connect(
            lambda: self._single_workers.remove(single_worker) if single_worker in self._single_workers else None
        )

    def _remove_task(self, task_id: str):
        task = next((t for t in self.tasks if t.task_id == task_id), None)
        if task:
            task.release()
        self.tasks = [t for t in self.tasks if t.task_id != task_id]
        self.task_table.remove_task_row(task_id)
        if not self.tasks:
            self.preview_card.reset_to_empty()
            self.process_bar.reset_to_idle()
        self._update_status_bar()

    def _preview_file(self, filepath: str):
        # Charger dans la carte d'inspection locale
        self.preview_card.load_media(filepath)
        # Ouvrir le lecteur Plein Écran Haute Fidélité
        from .fullscreen_player import FullScreenStudioPlayer
        fs = FullScreenStudioPlayer(filepath, auto_play=True, parent=self)
        fs.showFullScreen()

    def _clear_tasks(self):
        for task in self.tasks:
            task.release()
        clear_allocated_output_paths()
        self.tasks.clear()
        self.task_table.setRowCount(0)
        self.task_table.tasks_map.clear()
        self.task_table.convert_buttons.clear()
        self.preview_card.reset_to_empty()
        self.process_bar.reset_to_idle()
        # Réinitialise la Partie 2 (Étape 2) sur son mode par défaut : Vidéo MP4
        self.preset_panel.reset_to_default()
        self._update_status_bar()

    def _change_output_directory(self):
        folder = QFileDialog.getExistingDirectory(self, "Choisir le dossier de sortie", self.output_directory)
        if folder:
            self.output_directory = set_output_dir(folder)
            self.lbl_dest_info.setText(f"📁 {Path(folder).name}")
            self.lbl_dest_info.setToolTip(folder)
            self._update_status_bar()

    def _open_about(self):
        dlg = AboutDialog(self)
        dlg.exec()

    def _toggle_theme(self):
        """Bascule dynamiquement entre le Thème Clair et le Thème Sombre."""
        self.is_light_mode = not self.is_light_mode
        self._apply_current_theme()

    def _apply_current_theme(self):
        """Applique la feuille de style et rafraîchit tous les composants interactifs."""
        from .theme import get_theme_stylesheet
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if app:
            app.setStyleSheet(get_theme_stylesheet(self.is_light_mode))
        self.cyber_bg.set_light_mode(self.is_light_mode)
        self.task_table.set_light_mode(self.is_light_mode)
        if hasattr(self, "process_bar"):
            self.process_bar.set_light_mode(self.is_light_mode)
        self.btn_theme_toggle.setText(tr("theme_dark") if self.is_light_mode else tr("theme_light"))
        self._update_header_logo()

    def _update_header_logo(self):
        """Met à jour l'emblème haute définition, le titre et la description selon le thème."""
        if not hasattr(self, "lbl_logo_emblem"):
            return

        # 1. Emblème officiel 3D haute résolution (glc_logo.png / glc_logo_512.png)
        logo_file = LOGO_PATH if LOGO_PATH.exists() else LOGO_512_PATH
        if logo_file.exists():
            pix = QPixmap(str(logo_file)).scaled(
                54, 54,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.lbl_logo_emblem.setPixmap(pix)

        # 2. Typographie Vectorielle Haute Définition (100% nette, zéro flou)
        if self.is_light_mode:
            self.lbl_brand_title.setText(
                '<span style="color: #7c3aed; font-weight: 900; font-size: 22px; letter-spacing: 1px;">GLC</span> '
                '<span style="color: #0f172a; font-weight: 900; font-size: 22px; letter-spacing: 2px;">CONVERTER</span>'
            )
            self.lbl_brand_desc.setStyleSheet(
                "color: #475569; font-size: 11px; font-weight: 600; letter-spacing: 0.3px;"
            )
        else:
            self.lbl_brand_title.setText(
                '<span style="color: #c084fc; font-weight: 900; font-size: 22px; letter-spacing: 1px;">GLC</span> '
                '<span style="color: #ffffff; font-weight: 900; font-size: 22px; letter-spacing: 2px;">CONVERTER</span>'
            )
            self.lbl_brand_desc.setStyleSheet(
                "color: #e2e8f0; font-size: 11px; font-weight: 600; letter-spacing: 0.3px;"
            )

        self.lbl_brand_desc.setText(
            f"{tr('app_subtitle') or 'Convertisseur Universel Ultime'} • {COMPANY_NAME}"
        )

    def _update_status_bar(self):
        total = len(self.tasks)
        done = sum(1 for t in self.tasks if t.status == "Terminé")
        
        # Télémétrie CPU/RAM légère et discrète
        try:
            cpu_pct = int(psutil.cpu_percent())
            ram_pct = int(psutil.virtual_memory().percent)
        except Exception:
            cpu_pct, ram_pct = 0, 0

        accel_tag = tr("status_gpu_active") if (self.hw.nvenc_available or self.hw.qsv_available) else tr("status_cpu_active")
        reminder = tr("status_step1_reminder")
        queue_txt = tr("status_queue", done=done, total=total)
        folder_label = tr("status_folder")
        status_text = (
            f"  ⚡ {APP_NAME} v{APP_VERSION}  |  "
            f"{reminder}  |  "
            f"{queue_txt}  |  "
            f"CPU: {cpu_pct}%  RAM: {ram_pct}%  |  "
            f"{accel_tag}  |  "
            f"{folder_label} {self.output_directory}"
        )
        self.status_bar.showMessage(status_text)

    def retranslate_ui(self, lang_code: str = None):
        """Met à jour instantanément la fenêtre principale lors d'un changement de langue."""
        self.setWindowTitle(f"{APP_NAME} — {tr('app_subtitle')} ({COMPANY_NAME})")
        if hasattr(self, "lbl_brand_desc"):
            self.lbl_brand_desc.setText(f"{tr('app_subtitle') or 'Convertisseur Universel Ultime'} • {COMPANY_NAME}")
        self.btn_theme_toggle.setText(tr("theme_dark") if self.is_light_mode else tr("theme_light"))
        if hasattr(self, "btn_web"):
            self.btn_web.setText(tr("website_btn"))
        if hasattr(self, "btn_about"):
            self.btn_about.setText(tr("about"))
        if hasattr(self, "cb_lang"):
            curr_code = I18nManager.get_instance().get_language()
            self.cb_lang.blockSignals(True)
            for idx in range(self.cb_lang.count()):
                if self.cb_lang.itemData(idx) == curr_code:
                    self.cb_lang.setCurrentIndex(idx)
                    break
            self.cb_lang.blockSignals(False)
            self.cb_lang.setToolTip(tr("lang_selector"))
        if hasattr(self, "lbl_step3"):
            self.lbl_step3.setText(tr("step3_title"))
        if hasattr(self, "btn_chg_dest"):
            self.btn_chg_dest.setText(tr("change_dest"))
        if hasattr(self, "btn_start"):
            is_busy = getattr(self, "worker", None) and self.worker.isRunning()
            self.btn_start.setText(tr("btn_converting") if is_busy else tr("btn_convert_all"))
        if hasattr(self, "btn_clear"):
            cur_lang = (lang_code or getattr(I18nManager.get_instance(), "current_lang", "fr")).lower()
            if "ht" in cur_lang:
                self.btn_clear.setText("🗑️ Vide")
            elif "en" in cur_lang:
                self.btn_clear.setText("🗑️ Clear")
            elif "es" in cur_lang:
                self.btn_clear.setText("🗑️ Vaciar")
            else:
                self.btn_clear.setText("🗑️ Vider")
            self.btn_clear.setToolTip(tr("btn_clear_tooltip"))
        if hasattr(self, "btn_html"):
            self.btn_html.setText("⚡ HTML")
            self.btn_html.setToolTip(tr("btn_html_tooltip"))
        if hasattr(self, "btn_github"):
            self.btn_github.setText(tr("github_btn"))
            self.btn_github.setToolTip(tr("github_tooltip"))
        self._update_status_bar()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        w = self.width()
        if hasattr(self, "lbl_brand_desc") and hasattr(self, "btn_web"):
            if w < 1120:
                self.lbl_brand_desc.setVisible(False)
            else:
                self.lbl_brand_desc.setVisible(True)

            if w < 1040:
                self.btn_web.setText("🌐 GRAN LAKU")
            else:
                self.btn_web.setText(tr("website_btn"))

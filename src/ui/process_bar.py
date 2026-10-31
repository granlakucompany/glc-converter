"""
GLC CONVERTER — Barre de Progression Studio Haute Technologie
Éditeur: GRAN LAKU COMPANY | https://granlaku.com/glcconverter

Affiche en temps réel :
- Dégradé Mauve & Bleu fondu ensemble (Cyber Glow)
- Détails de la conversion en cours (nom de fichier, étape, codecs)
- Pourcentage précis (%)
- Temps écoulé et temps restant calculé en minutes et secondes
"""
import time
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QWidget
)
from PySide6.QtGui import QFont

from ..core.converter_engine import ConversionTask
from ..core.i18n import I18nManager, tr

class ProcessProgressBar(QFrame):
    """
    Barre de processus globale de studio située dans le bas de l'application.
    Met en valeur le dégradé fusionné Mauve & Bleu, la télémétrie en minutes/secondes,
    et les détails textuels de chaque phase d'encodage.
    """

    def __init__(self, is_light_mode: bool = False, parent=None):
        super().__init__(parent)
        self.is_light_mode = is_light_mode
        self.setObjectName("bottomProcessPanel")

        self.start_time: Optional[float] = None
        self.total_tasks_count = 0
        self.completed_tasks_count = 0
        self.current_task_name = ""
        self.is_active = False

        self._timer = QTimer(self)
        self._timer.setInterval(500)  # Rafraîchissement du chronomètre toutes les 500ms
        self._timer.timeout.connect(self._on_tick_time)

        self._setup_ui()
        self.reset_to_idle()
        I18nManager.get_instance().register_listener(self.retranslate_ui)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 4, 12, 6)
        layout.setSpacing(4)

        # Ligne Supérieure : Détails de la tâche (Gauche) + Minuteur & Durée (Droite)
        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)

        # Détails de l'opération en cours
        self.lbl_details = QLabel("💡 Prêt • En attente de conversion")
        self.lbl_details.setObjectName("processDetailLabel")
        top_row.addWidget(self.lbl_details, stretch=1)

        # Minuteur : Minutes écoulées & Minutes restantes
        self.lbl_time = QLabel("⏱️ 00m 00s")
        self.lbl_time.setObjectName("processTimeLabel")
        self.lbl_time.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        top_row.addWidget(self.lbl_time, stretch=0)

        layout.addLayout(top_row)

        # Barre de Progression avec dégradé Mauve & Bleu
        self.pbar = QProgressBar()
        self.pbar.setObjectName("bottomProcessBar")
        self.pbar.setFixedHeight(20)
        self.pbar.setRange(0, 100)
        self.pbar.setValue(0)
        self.pbar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pbar.setFormat("%p%")

        layout.addWidget(self.pbar)

    def set_light_mode(self, is_light: bool):
        self.is_light_mode = is_light
        self._apply_style()

    def _apply_style(self):
        """Met à jour les styles dynamiques selon le mode sombre ou clair."""
        pass  # Les styles sont principalement gérés via QSS dans theme.py

    def reset_to_idle(self):
        """Réinitialise la barre en état d'attente (Standby)."""
        self.is_active = False
        self._timer.stop()
        self.start_time = None
        self.pbar.setValue(0)
        self.pbar.setFormat(f"{tr('status_waiting')} (0%)")
        self.lbl_details.setText(tr("process_ready"))
        self.lbl_time.setText("⏱️ 00m 00s")

    def start_process(self, total_tasks: int, first_task_name: str = ""):
        """Déclenche le suivi d'un nouveau lot de conversions."""
        self.is_active = True
        self.total_tasks_count = max(1, total_tasks)
        self.completed_tasks_count = 0
        self.start_time = time.time()
        self._timer.start()

        short_name = Path(first_task_name).name if first_task_name else "Média"
        self.lbl_details.setText(f"⚡ [1/{self.total_tasks_count}] {short_name}...")
        self.pbar.setValue(0)
        self.pbar.setFormat(f"0% • {tr('status_running')}...")
        self.lbl_time.setText(f"⏱️ 00m 00s {tr('process_elapsed')}")

    @staticmethod
    def _get_target_conversion_label(task: ConversionTask) -> str:
        """Détermine un libellé clair et valorisant du format/résolution cible (ex: 4K, 8K, PNG...)."""
        opts = task.options or {}
        res = opts.get("resolution")
        fmt = task.output_format.upper()

        # Résolution vidéo spécifique
        res_label = ""
        if res:
            if "12288" in res or "11520" in res:
                res_label = "12K Ultra-HD"
            elif "7680" in res:
                res_label = "8K UHD"
            elif "3840" in res:
                res_label = "4K UHD"
            elif "1920x1080" in res or ("1080" in res and "1920" not in res):
                res_label = "1080p Full HD"
            elif "1080x1920" in res:
                res_label = "9:16 Vertical (Reels/TikTok)"
            elif "1280x720" in res:
                res_label = "720p HD"
            else:
                res_label = res

        cat = (task.file_info.get("category") if task.file_info else "") or ""
        cat = cat.lower()

        if res_label:
            return f"{res_label} ({fmt})"
        elif fmt in ["PNG", "WEBP", "JPG", "JPEG", "AVIF", "TIFF", "BMP", "ICO"]:
            if fmt == "PNG":
                return "PNG (Lossless)"
            elif fmt == "WEBP":
                return "WebP Haute Résolution"
            return f"Image {fmt}"
        elif fmt in ["MP3", "WAV", "FLAC", "AAC", "OGG", "OPUS"]:
            bitrate = opts.get("bitrate", "320k")
            return f"Audio {fmt} ({bitrate})"
        elif fmt in ["PDF", "TXT", "DOCX"]:
            return f"Document {fmt}"
        elif fmt in ["MP4", "MKV", "WEBM", "MOV", "PRORES"]:
            return f"Vidéo {fmt}"
        return f"{fmt}"

    def update_task_progress(self, task: ConversionTask, current_idx: int = 1, total_count: int = 1):
        """Met à jour les détails en temps réel et le pourcentage global."""
        if not self.is_active:
            self.start_process(total_count, task.input_path)

        file_name = Path(task.input_path).name
        target_desc = self._get_target_conversion_label(task)

        # Calcul du pourcentage global lissé
        base_progress = ((current_idx - 1) / total_count) * 100.0
        task_slice = (task.progress / 100.0) * (100.0 / total_count)
        global_pct = min(100.0, max(0.0, base_progress + task_slice))

        self.pbar.setValue(int(global_pct))

        speed_info = f" • {task.speed:.0f} fps" if task.speed > 0 else ""
        self.pbar.setFormat(f"{int(global_pct)}%  ({current_idx}/{total_count}){speed_info}")

        # Détail textuel explicite de l'opération en cours avec nom unique de sortie et code GLC
        out_name = Path(task.output_path).name
        self.lbl_details.setText(
            f"⚡ [{current_idx}/{total_count}] {file_name} → {out_name} • En cours de conversion en {target_desc}{speed_info}"
        )

        self._update_time_display(global_pct)

    def on_task_completed(self, task: ConversionTask, completed_count: int, total_count: int):
        """Notifie la fin d'une tâche individuelle."""
        self.completed_tasks_count = completed_count
        out_name = Path(task.output_path).name
        target_desc = self._get_target_conversion_label(task)
        code_str = f" [Code: {task.unique_code}]" if hasattr(task, "unique_code") else ""
        self.lbl_details.setText(f"✓ [{completed_count}/{total_count}] {out_name}{code_str} • Converti avec succès en {target_desc}")

    def finish_process(self, success: bool = True):
        """Finalise le suivi lorsque toutes les tâches sont achevées."""
        self.is_active = False
        self._timer.stop()

        elapsed = time.time() - self.start_time if self.start_time else 0.0
        mins = int(elapsed // 60)
        secs = int(elapsed % 60)
        time_str = f"{mins:02d}m {secs:02d}s"

        self.pbar.setValue(100)
        if success:
            self.pbar.setFormat(tr("process_success"))
            self.lbl_details.setText(tr("process_all_done"))
            self.lbl_time.setText(f"{tr('process_total_time')} {time_str}")
        else:
            self.pbar.setFormat(tr("status_error"))
            self.lbl_details.setText(tr("process_error"))
            self.lbl_time.setText(f"⏱️ {time_str}")

    def _on_tick_time(self):
        """Met à jour le chronomètre d'exécution et l'estimation du temps restant."""
        if not self.is_active or self.start_time is None:
            return
        
        current_val = self.pbar.value()
        self._update_time_display(current_val)

    def _update_time_display(self, current_pct: float):
        if self.start_time is None:
            return

        elapsed = max(0.1, time.time() - self.start_time)
        e_mins = int(elapsed // 60)
        e_secs = int(elapsed % 60)
        elapsed_str = f"{e_mins:02d}m {e_secs:02d}s"

        if current_pct > 2.0 and current_pct < 99.0:
            total_est = elapsed / (current_pct / 100.0)
            remaining = max(0.0, total_est - elapsed)
            r_mins = int(remaining // 60)
            r_secs = int(remaining % 60)
            self.lbl_time.setText(f"⏱️ {elapsed_str} {tr('process_elapsed')}  •  ~{r_mins:02d}m {r_secs:02d}s {tr('process_remaining')}")
        elif current_pct >= 99.0:
            self.lbl_time.setText(f"⏱️ {elapsed_str} {tr('process_elapsed')}  •  {tr('process_finalizing')}")
        else:
            self.lbl_time.setText(f"⏱️ {elapsed_str} {tr('process_elapsed')}")

    def retranslate_ui(self, lang_code: str = None):
        """Rafraîchit les textes selon la langue active."""
        if not self.is_active:
            if self.pbar.value() == 0:
                self.reset_to_idle()
            elif self.pbar.value() == 100:
                self.pbar.setFormat(tr("process_success"))
                self.lbl_details.setText(tr("process_all_done"))

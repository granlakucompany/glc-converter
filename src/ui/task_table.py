"""
GLC CONVERTER — Tableau de File d'Attente des Tâches (Thème Clair & Thème Sombre)
Éditeur: GRAN LAKU COMPANY | https://granlaku.com/glcconverter
"""
import os
import math
import subprocess
from pathlib import Path
from typing import List, Optional, Dict

from PySide6.QtCore import Qt, Signal, QTimer, QPointF, QRectF
from PySide6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QHeaderView, QProgressBar,
    QWidget, QHBoxLayout, QPushButton, QLabel, QCheckBox
)
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QPolygonF, QLinearGradient

from ..core.converter_engine import ConversionTask
from ..core.i18n import I18nManager, tr


class SpinningConvertButton(QPushButton):
    """
    Bouton d'action de conversion avec rotation continue animée
    lorsque la tâche est en cours d'exécution (« ti icon nan dwe ap vire won »).
    """
    def __init__(self, is_light_mode: bool = False, parent=None):
        super().__init__(parent)
        self.is_light_mode = is_light_mode
        self.setObjectName("btnConvertSingle")
        self.setToolTip(tr("act_convert_tooltip"))
        self.setFixedSize(24, 24)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._angle = 0
        self._is_spinning = False
        self._timer = QTimer(self)
        self._timer.setInterval(33)  # ~30 FPS
        self._timer.timeout.connect(self._on_tick)

    def set_light_mode(self, is_light: bool):
        self.is_light_mode = is_light
        self.update()

    def start_spinning(self):
        self._is_spinning = True
        self.setToolTip(tr("btn_converting"))
        if not self._timer.isActive():
            self._timer.start()
        self.update()

    def stop_spinning(self):
        self._is_spinning = False
        self._timer.stop()
        self._angle = 0
        self.setToolTip(tr("act_convert_tooltip"))
        self.update()

    def _on_tick(self):
        self._angle = (self._angle + 14) % 360
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        cx = self.width() / 2.0
        cy = self.height() / 2.0
        painter.translate(cx, cy)
        
        if self._is_spinning:
            # Mode rotation continue dynamique lors de la conversion active ("ti icon nan ap vire won")
            painter.rotate(self._angle)
            pen_color = QColor("#06b6d4" if self.is_light_mode else "#38bdf8") if (self._angle % 90 > 45) else QColor("#7c3aed" if self.is_light_mode else "#c084fc")
            pen = QPen(pen_color, 2.2)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            
            r = 6.5
            painter.drawArc(int(-r), int(-r), int(2*r), int(2*r), 20 * 16, 130 * 16)
            painter.drawArc(int(-r), int(-r), int(2*r), int(2*r), 200 * 16, 130 * 16)
            
            painter.setBrush(pen.color())
            a1 = math.radians(150)
            x1 = r * math.cos(a1)
            y1 = -r * math.sin(a1)
            p1 = QPolygonF([
                QPointF(x1, y1),
                QPointF(x1 + 3.2, y1 - 2.8),
                QPointF(x1 + 0.6, y1 - 3.8)
            ])
            painter.drawPolygon(p1)

            a2 = math.radians(330)
            x2 = r * math.cos(a2)
            y2 = -r * math.sin(a2)
            p2 = QPolygonF([
                QPointF(x2, y2),
                QPointF(x2 - 3.2, y2 + 2.8),
                QPointF(x2 - 0.6, y2 + 3.8)
            ])
            painter.drawPolygon(p2)
        else:
            # Mode repos (En attente / Prêt) : Triangle de lecture Play ▶ net, éclatant et sans ambiguïté
            play_color = QColor("#ffffff" if not self.is_light_mode else "#581c87")
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(play_color)
            
            p_play = QPolygonF([
                QPointF(-3.0, -5.0),
                QPointF(5.0, 0.0),
                QPointF(-3.0, 5.0)
            ])
            painter.drawPolygon(p_play)


class TableActionButton(QPushButton):
    """
    Bouton d'action vectoriel haute technologie pour le tableau des tâches.
    Entièrement dessiné via QPainter avec lissage (Antialiasing) :
    - Garanti 100% visible, net et éclatant sur tous les écrans, tous les DPI et polices
    - Élimine tout risque d'icône manquante ou masquée par le moteur de police
    - Types d'icônes :
        * 'open'    : Icône Dossier dorée/ambrée vectorielle
        * 'preview' : Icône Loupe d'inspection cyan vectorielle
        * 'remove'  : Icône Croix ✕ blanche de suppression sur fond rouge
    """
    def __init__(self, action_type: str, is_light_mode: bool = False, parent=None):
        super().__init__(parent)
        self.action_type = action_type  # 'open', 'preview', 'remove'
        self.is_light_mode = is_light_mode
        self.setFixedSize(24, 24)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        if action_type == "remove":
            self.setObjectName("btnDanger")
            self.setToolTip(tr("act_remove_tooltip"))
        elif action_type == "open":
            self.setObjectName("btnTableAction")
            self.setToolTip(tr("act_open_tooltip"))
        elif action_type == "preview":
            self.setObjectName("btnTableAction")
            self.setToolTip(tr("act_preview_tooltip"))

    def set_light_mode(self, is_light: bool):
        self.is_light_mode = is_light
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        cx = self.width() / 2.0
        cy = self.height() / 2.0
        painter.translate(cx, cy)

        if self.action_type == "open":
            # Icône Dossier (Folder) vectorielle
            folder_color = QColor("#b45309" if self.is_light_mode else "#fbbf24")
            pen = QPen(folder_color, 1.4)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.setBrush(folder_color)

            # Onglet supérieur gauche
            tab = QPolygonF([
                QPointF(-6.0, -4.5),
                QPointF(-2.0, -4.5),
                QPointF(-0.8, -3.0),
                QPointF(-6.0, -3.0)
            ])
            painter.drawPolygon(tab)

            # Corps du dossier
            painter.drawRoundedRect(QRectF(-6.0, -3.0, 12.0, 8.0), 1.2, 1.2)

        elif self.action_type == "preview":
            # Icône Loupe d'inspection (Search/Preview) vectorielle cyan
            cyan_color = QColor("#0284c7" if self.is_light_mode else "#38bdf8")
            pen = QPen(cyan_color, 1.8)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)

            # Cercle de la lentille
            r = 3.8
            painter.drawEllipse(QPointF(-1.5, -1.5), r, r)

            # Manche à 45°
            painter.drawLine(QPointF(1.5, 1.5), QPointF(5.5, 5.5))

        elif self.action_type == "remove":
            # Icône Croix ✕ (Delete) vectorielle blanche
            cross_color = QColor("#ffffff" if not self.is_light_mode else "#991b1b")
            pen = QPen(cross_color, 2.0)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)

            s = 3.8
            painter.drawLine(QPointF(-s, -s), QPointF(s, s))
            painter.drawLine(QPointF(-s, s), QPointF(s, -s))


class CyberTableProgressBar(QProgressBar):
    """
    Barre de progression cybernétique pour cellule de tableau.
    Garantit un centrage mathématique absolu (horizontal et vertical) du conteneur
    et du texte de pourcentage, sans décalage ni dépendance aux anomalies de style d'OS.
    """

    def __init__(self, is_light_mode: bool = False, parent=None):
        super().__init__(parent)
        self.is_light_mode = is_light_mode
        self.setFixedHeight(18)
        self.setRange(0, 100)
        self.setTextVisible(False)
        self.setObjectName("tableProgressBar")

    def set_light_mode(self, is_light: bool):
        self.is_light_mode = is_light
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()

        r = 6.0
        w = rect.width()
        h = rect.height()

        # 1. Fond cyber arrondi
        bg_color = QColor("#e2e8f0") if self.is_light_mode else QColor("#090810")
        border_color = QColor("#cbd5e1") if self.is_light_mode else QColor(139, 92, 246, 120)

        pen = QPen(border_color, 1.0)
        painter.setPen(pen)
        painter.setBrush(bg_color)
        bg_rect = QRectF(0.5, 0.5, w - 1.0, h - 1.0)
        painter.drawRoundedRect(bg_rect, r, r)

        # 2. Remplissage (Chunk) avec dégradé cybernétique
        val = self.value()
        minimum = self.minimum()
        maximum = self.maximum()
        pct = 0.0
        if maximum > minimum:
            pct = max(0.0, min(1.0, (val - minimum) / (maximum - minimum)))

        if pct > 0:
            fill_w = max(r * 2, (w - 2.0) * pct)
            fill_rect = QRectF(1.0, 1.0, min(fill_w, w - 2.0), h - 2.0)

            grad = QLinearGradient(0, 0, w, 0)
            if self.is_light_mode:
                grad.setColorAt(0.0, QColor("#7c3aed"))
                grad.setColorAt(0.5, QColor("#8b5cf6"))
                grad.setColorAt(1.0, QColor("#a855f7"))
            else:
                grad.setColorAt(0.0, QColor("#581c87"))
                grad.setColorAt(0.35, QColor("#7c3aed"))
                grad.setColorAt(0.75, QColor("#9333ea"))
                grad.setColorAt(1.0, QColor("#c084fc"))

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(grad)
            painter.drawRoundedRect(fill_rect, r - 1.0, r - 1.0)

        # 3. Texte du pourcentage parfaitement centré au pixel près (horizontal & vertical)
        font = QFont("Segoe UI", 8, QFont.Weight.Bold)
        painter.setFont(font)
        text = f"{val}%"

        if not self.is_light_mode:
            # Ombre portée douce pour lisibilité parfaite quel que soit le niveau de progression
            painter.setPen(QColor(0, 0, 0, 200))
            painter.drawText(rect.adjusted(1, 1, 1, 1), Qt.AlignmentFlag.AlignCenter, text)
            painter.setPen(QColor("#ffffff"))
        else:
            painter.setPen(QColor("#ffffff" if pct > 0.45 else "#0f172a"))

        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)


class TaskTableWidget(QTableWidget):
    """
    Tableau listant les tâches de conversion avec :
    - Case à cocher carrée ("ti kare") devant chaque fichier pour sélectionner avant conversion
    - Bascule "Tout Sélectionner / Désélectionner" via clic sur l'en-tête [✓]
    - En-têtes et textes parfaitement centrés
    - Bouton individuel de conversion rotatif (« ti icon nan dwe ap vire won »)
    - Gestion responsive pour que toutes les icônes et menus d'actions soient TOUJOURS visibles
    - Support complet Thème Clair et Thème Sombre
    """

    task_remove_requested = Signal(str)
    task_convert_single = Signal(str)
    task_selection_changed = Signal(str, bool)
    preview_requested = Signal(str)

    COLUMN_KEYS = [
        "col_select",
        "col_file",
        "col_source",
        "col_target",
        "col_size",
        "col_progress",
        "col_speed",
        "col_status",
        "col_actions"
    ]

    def __init__(self, parent=None, is_light_mode: bool = False):
        super().__init__(parent)
        self.is_light_mode = is_light_mode
        self._all_checked = True
        self.convert_buttons: Dict[str, SpinningConvertButton] = {}
        self.tasks_map = {}  # task_id -> row_index

        self.setColumnCount(len(self.COLUMN_KEYS))
        self.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # En-têtes centrés avec typographie haute précision
        for col_idx, col_key in enumerate(self.COLUMN_KEYS):
            header_item = QTableWidgetItem(tr(col_key))
            header_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if col_idx == 0:
                header_item.setToolTip(tr("select_all_tooltip"))
            self.setHorizontalHeaderItem(col_idx, header_item)

        # Calibrage strict des colonnes pour un affichage parfait et sans troncature des actions
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Fichier s'étend avec priorité
        header.setStretchLastSection(False)

        self.setColumnWidth(0, 30)   # Colonne case à cocher carrée
        # Col 1: Stretch (Fichier - large et lisible)
        self.setColumnWidth(2, 50)   # Source (ex: "HTML", "WEBM", "MP4")
        self.setColumnWidth(3, 85)   # Format Cible (ex: "➜ WEBP", "➜ MP4")
        self.setColumnWidth(4, 64)   # Taille (ex: "172.4 KB", "148.5 Mo")
        self.setColumnWidth(5, 80)   # Progression (Barre + %)
        self.setColumnWidth(6, 62)   # Vitesse (ex: "60.0 fps")
        self.setColumnWidth(7, 78)   # Statut (ex: "En attente", "En cours", "Terminé")
        self.setColumnWidth(8, 112)  # Actions (4 boutons de 24px : [▶] [📁] [🔍] [✕])

        self.verticalHeader().setVisible(False)
        self.verticalHeader().setDefaultSectionSize(42)  # Hauteur aérée de 42px pour chaque ligne de tâche
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setAlternatingRowColors(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setTextElideMode(Qt.TextElideMode.ElideMiddle)

        # Clic sur l'en-tête de sélection pour tout cocher/décocher
        self.horizontalHeader().sectionClicked.connect(self._on_header_section_clicked)
        I18nManager.get_instance().register_listener(self.retranslate_ui)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Toutes les colonnes (y compris Vitesse, Source et Statut) restent toujours visibles !

    def _on_header_section_clicked(self, logical_index: int):
        if logical_index == 0:
            self._all_checked = not self._all_checked
            self.toggle_all_checked(self._all_checked)

    def set_light_mode(self, is_light: bool):
        self.is_light_mode = is_light
        for btn in self.convert_buttons.values():
            btn.set_light_mode(is_light)

        # Mettre à jour les couleurs des éléments existants
        for row in range(self.rowCount()):
            target_item = self.item(row, 3)
            if target_item:
                target_item.setForeground(QColor("#7c3aed" if self.is_light_mode else "#c084fc"))
            status_item = self.item(row, 7)
            if status_item:
                status_text = status_item.text()
                if status_text == "Terminé":
                    status_item.setForeground(QColor("#059669" if self.is_light_mode else "#34d399"))
                elif status_text == "Erreur":
                    status_item.setForeground(QColor("#dc2626" if self.is_light_mode else "#f87171"))
                elif status_text == "En cours":
                    status_item.setForeground(QColor("#7c3aed" if self.is_light_mode else "#c084fc"))
            act_w = self.cellWidget(row, 8)
            if act_w:
                for b in act_w.findChildren(TableActionButton):
                    b.set_light_mode(is_light)
            pbar_w = self.cellWidget(row, 5)
            if pbar_w:
                for pb in pbar_w.findChildren(CyberTableProgressBar):
                    pb.set_light_mode(is_light)

    def add_task(self, task: ConversionTask):
        row = self.rowCount()
        self.insertRow(row)
        self.tasks_map[task.task_id] = row

        # 0: Case à cocher carrée ("ti kare") centrée
        chk_widget = QWidget()
        chk_layout = QHBoxLayout(chk_widget)
        chk_layout.setContentsMargins(0, 4, 0, 4)
        chk_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cb = QCheckBox()
        cb.setChecked(True)
        cb.setToolTip("Cocher pour inclure ce fichier dans la conversion")
        cb.stateChanged.connect(
            lambda state, tid=task.task_id: self.task_selection_changed.emit(tid, state == Qt.CheckState.Checked.value)
        )
        chk_layout.addWidget(cb)
        self.setCellWidget(row, 0, chk_widget)

        # 1: Fichier (Centré, avec infobulle du chemin complet, fichier unique et code GLC)
        unique_code = getattr(task, "unique_code", task.task_id[:8].upper())
        out_name = Path(task.output_path).name
        raw_name = task.file_info.get("name") or Path(task.input_path).name or task.input_path
        name_item = QTableWidgetItem(raw_name)
        name_item.setToolTip(f"Source : {task.input_path}\nFichier de sortie : {out_name}\nCode unique GLC : {unique_code}")
        name_item.setData(Qt.ItemDataRole.UserRole, task.task_id)
        name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setItem(row, 1, name_item)

        # 2: Format Source (Centré)
        src_fmt = task.file_info.get("extension", "").upper()
        src_item = QTableWidgetItem(src_fmt)
        src_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        src_item.setForeground(QColor("#64748b" if self.is_light_mode else "#94a3b8"))
        self.setItem(row, 2, src_item)

        # 3: Format Cible avec Flèche fine et couleur vive (Centré)
        target_str = f"➜ {task.output_format.upper()}"
        target_item = QTableWidgetItem(target_str)
        target_item.setToolTip(f"Format cible : {task.output_format.upper()}\nCode unique : {unique_code}\nFichier généré : {out_name}")
        target_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        target_item.setForeground(QColor("#7c3aed" if self.is_light_mode else "#c084fc"))
        target_font = QFont("Segoe UI", 9, QFont.Weight.Bold)
        target_item.setFont(target_font)
        self.setItem(row, 3, target_item)

        # 4: Taille (Centrée)
        size_str = task.file_info.get("size_formatted", "")
        size_item = QTableWidgetItem(size_str)
        size_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setItem(row, 4, size_item)

        # 5: Barre de Progression Cybernétique (Centrée verticalement et horizontalement)
        pbar_widget = QWidget()
        pbar_layout = QHBoxLayout(pbar_widget)
        pbar_layout.setContentsMargins(6, 4, 6, 4)
        pbar_layout.setSpacing(0)
        pbar_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        pbar = CyberTableProgressBar(is_light_mode=self.is_light_mode)
        pbar.setValue(int(task.progress))
        pbar_layout.addWidget(pbar)
        self.setCellWidget(row, 5, pbar_widget)

        # 6: Vitesse (Centrée)
        speed_item = QTableWidgetItem("--")
        speed_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setItem(row, 6, speed_item)

        # 7: Statut Badge (Centré)
        status_text = self._translate_status(task.status)
        status_item = QTableWidgetItem(status_text)
        status_item.setData(Qt.ItemDataRole.UserRole, task.status)
        status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        if task.status == "Terminé":
            status_item.setForeground(QColor("#059669" if self.is_light_mode else "#34d399"))
            unique_code = getattr(task, "unique_code", task.task_id[:8].upper())
            status_item.setToolTip(f"Terminé avec succès !\nFichier : {Path(task.output_path).name}\nCode unique GLC : {unique_code}")
        elif task.status == "Erreur":
            status_item.setForeground(QColor("#dc2626" if self.is_light_mode else "#f87171"))
        elif task.status == "En cours":
            status_item.setForeground(QColor("#7c3aed" if self.is_light_mode else "#c084fc"))
        self.setItem(row, 7, status_item)

        # 8: Actions Widget (Convertir individuellement avec rotation / Ouvrir / Prévisualiser / Supprimer)
        action_widget = QWidget()
        act_layout = QHBoxLayout(action_widget)
        act_layout.setContentsMargins(2, 2, 2, 2)
        act_layout.setSpacing(3)
        act_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Bouton individuel de conversion avec animation de rotation (Play ▶ en attente, rotation en cours)
        btn_convert = SpinningConvertButton(is_light_mode=self.is_light_mode)
        btn_convert.clicked.connect(lambda _, tid=task.task_id: self.task_convert_single.emit(tid))
        act_layout.addWidget(btn_convert)
        self.convert_buttons[task.task_id] = btn_convert

        # Bouton ouvrir dossier (TableActionButton vectoriel)
        btn_open = TableActionButton("open", is_light_mode=self.is_light_mode)
        btn_open.clicked.connect(lambda _, t=task: self._open_task_location(t))
        act_layout.addWidget(btn_open)

        # Bouton aperçu / inspecter (TableActionButton vectoriel)
        btn_preview = TableActionButton("preview", is_light_mode=self.is_light_mode)
        btn_preview.clicked.connect(lambda _, p=task.input_path: self.preview_requested.emit(p))
        act_layout.addWidget(btn_preview)

        # Bouton supprimer (TableActionButton vectoriel)
        btn_remove = TableActionButton("remove", is_light_mode=self.is_light_mode)
        btn_remove.clicked.connect(lambda _, tid=task.task_id: self.task_remove_requested.emit(tid))
        act_layout.addWidget(btn_remove)

        self.setCellWidget(row, 8, action_widget)

    def is_task_checked(self, row: int) -> bool:
        """Indique si la case à cocher de la ligne est active."""
        widget = self.cellWidget(row, 0)
        if widget:
            cb = widget.findChild(QCheckBox)
            if cb:
                return cb.isChecked()
        return True

    def set_task_checked(self, row: int, checked: bool):
        """Active ou désactive la case à cocher de la ligne."""
        widget = self.cellWidget(row, 0)
        if widget:
            cb = widget.findChild(QCheckBox)
            if cb:
                cb.setChecked(checked)

    def get_checked_task_ids(self) -> List[str]:
        """Retourne la liste des task_id dont la case est cochée."""
        checked_ids = []
        for r in range(self.rowCount()):
            if self.is_task_checked(r):
                item = self.item(r, 1)
                if item:
                    tid = item.data(Qt.ItemDataRole.UserRole)
                    if tid:
                        checked_ids.append(tid)
        return checked_ids

    def toggle_all_checked(self, checked: bool):
        """Coche ou décoche toutes les cases de la file."""
        for r in range(self.rowCount()):
            self.set_task_checked(r, checked)

    def update_task_progress(self, task: ConversionTask):
        row = self.tasks_map.get(task.task_id)
        if row is None or row >= self.rowCount():
            return

        # Gestion de l'animation de rotation de l'icône de conversion
        btn_conv = self.convert_buttons.get(task.task_id)
        if btn_conv:
            if task.status == "En cours":
                btn_conv.start_spinning()
            else:
                btn_conv.stop_spinning()

        # Mise à jour de la barre de progression (col 5)
        cell_w = self.cellWidget(row, 5)
        if isinstance(cell_w, QProgressBar):
            cell_w.setValue(int(task.progress))
        elif cell_w:
            pbar = cell_w.findChild(QProgressBar)
            if pbar:
                pbar.setValue(int(task.progress))

        # Format cible (col 3)
        tgt_item = self.item(row, 3)
        if tgt_item:
            tgt_item.setText(f"➜ {task.output_format.upper()}")
            tgt_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            tgt_item.setForeground(QColor("#7c3aed" if self.is_light_mode else "#c084fc"))

        # Vitesse / ETA (col 6)
        speed_txt = f"{task.speed:.1f} fps" if task.speed > 0 else "--"
        if task.eta != "--:--":
            speed_txt += f" ({task.eta})"
        speed_item = QTableWidgetItem(speed_txt)
        speed_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setItem(row, 6, speed_item)

        # Statut (col 7)
        status_item = self.item(row, 7)
        if not status_item:
            status_item = QTableWidgetItem()
            self.setItem(row, 7, status_item)
        status_item.setData(Qt.ItemDataRole.UserRole, task.status)
        status_item.setText(self._translate_status(task.status))
        status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        if task.status == "Terminé":
            status_item.setForeground(QColor("#059669" if self.is_light_mode else "#34d399"))
            unique_code = getattr(task, "unique_code", task.task_id[:8].upper())
            status_item.setToolTip(f"Terminé avec succès !\nFichier : {Path(task.output_path).name}\nCode unique GLC : {unique_code}")
        elif task.status == "Erreur":
            status_item.setForeground(QColor("#dc2626" if self.is_light_mode else "#f87171"))
            status_item.setToolTip(task.error_message)
        elif task.status == "En cours":
            status_item.setForeground(QColor("#7c3aed" if self.is_light_mode else "#c084fc"))

    def _translate_status(self, raw_status: str) -> str:
        status_map = {
            "En attente": "status_waiting",
            "En cours": "status_running",
            "Terminé": "status_completed",
            "Erreur": "status_error",
            "Annulé": "status_cancelled",
        }
        key = status_map.get(raw_status)
        return tr(key) if key else raw_status

    def retranslate_ui(self, lang_code: str = None):
        """Met à jour instantanément les colonnes, statuts et infobulles."""
        for col_idx, col_key in enumerate(self.COLUMN_KEYS):
            item = self.horizontalHeaderItem(col_idx)
            if item:
                item.setText(tr(col_key))
                if col_idx == 0:
                    item.setToolTip(tr("select_all_tooltip"))

        # Rafraîchir les statuts de chaque ligne
        for r in range(self.rowCount()):
            status_item = self.item(r, 7)
            if status_item:
                raw_st = status_item.data(Qt.ItemDataRole.UserRole)
                if raw_st:
                    status_item.setText(self._translate_status(raw_st))

            # Rafraîchir les infobulles des boutons d'action
            act_w = self.cellWidget(r, 8)
            if act_w:
                btns = act_w.findChildren(QPushButton)
                for b in btns:
                    if isinstance(b, SpinningConvertButton):
                        if not b._is_spinning:
                            b.setToolTip(tr("act_convert_tooltip"))
                        else:
                            b.setToolTip(tr("btn_converting"))
                    elif isinstance(b, TableActionButton):
                        if b.action_type == "open":
                            b.setToolTip(tr("act_open_tooltip"))
                        elif b.action_type == "preview":
                            b.setToolTip(tr("act_preview_tooltip"))
                        elif b.action_type == "remove":
                            b.setToolTip(tr("act_remove_tooltip"))
                    elif b.text() == "📁":
                        b.setToolTip(tr("act_open_tooltip"))
                    elif b.text() in ["🔍", "👁️", "👁"]:
                        b.setToolTip(tr("act_preview_tooltip"))
                    elif b.text() == "✕":
                        b.setToolTip(tr("act_remove_tooltip"))

    def remove_task_row(self, task_id: str):
        btn = self.convert_buttons.pop(task_id, None)
        if btn:
            btn.stop_spinning()

        row = self.tasks_map.get(task_id)
        if row is not None and row < self.rowCount():
            self.removeRow(row)
            self._rebuild_tasks_map()

    def _rebuild_tasks_map(self):
        self.tasks_map.clear()
        for r in range(self.rowCount()):
            item = self.item(r, 1)  # Nom du fichier en col 1
            if item:
                tid = item.data(Qt.ItemDataRole.UserRole)
                if tid:
                    self.tasks_map[tid] = r

    def _open_task_location(self, task: ConversionTask):
        target_path = task.output_path if Path(task.output_path).exists() else task.input_path
        if Path(target_path).exists():
            subprocess.Popen(f'explorer /select,"{os.path.abspath(target_path)}"')

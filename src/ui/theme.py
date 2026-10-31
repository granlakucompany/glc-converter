"""
GLC CONVERTER — Système de Thèmes : Thème Clair Studio & Thème Sombre
Éditeur: GRAN LAKU COMPANY | https://granlaku.com/glcconverter
"""

# ==============================================================================
# THÈME CLAIR STUDIO (LIGHT THEME) — PAR DÉFAUT (nap theme clair tout)
# Palette : Fond Blanc/Ardoise Clair, Boutons Mauve Foncé, Accents Mauve
# ==============================================================================
LIGHT_THEME_STYLE = """
QMainWindow {
    background-color: #f8fafc;
}

QWidget {
    color: #0f172a;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    font-size: 13px;
}

/* En-tête Principal Blanc Pur avec Accent Liseré Mauve */
#headerFrame {
    background: #ffffff;
    border-bottom: 2px solid #7c3aed;
    padding: 10px 20px;
}

QLabel#headerStudioBadge {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7c3aed, stop:1 #9333ea);
    color: #ffffff;
    font-size: 10px;
    font-weight: 800;
    padding: 3px 8px;
    border-radius: 6px;
    letter-spacing: 1px;
}

#headerTitle {
    color: #0f172a;
    font-size: 22px;
    font-weight: 900;
    letter-spacing: 0.8px;
}

#headerSubtitle {
    color: #6b21a8;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.4px;
}

/* Cartes Didactiques Blanc Pur avec Accents Bordures Mauve Délicates */
#cardFrame, #presetPanel, #mediaPreviewCard, QGroupBox {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 0px;
}

/* Zone de Dépôt Étape 1 */
#dropZone {
    background-color: #faf5ff;
    border: 2px dashed #a855f7;
    border-radius: 12px;
    padding: 0px;
}

#dropZone[dragActive="true"] {
    background-color: #f3e8ff;
    border: 2px dashed #7c3aed;
}

#dropTitle {
    font-size: 17px;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: 0.4px;
}

#dropSub {
    font-size: 12px;
    color: #475569;
    font-weight: 600;
    letter-spacing: 0.3px;
}

/* Badges d'Étapes Didactiques */
QLabel#stepBadge, .stepBadge {
    color: #581c87;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.8px;
    background: #f3e8ff;
    border: 1px solid #d8b4fe;
    border-radius: 4px;
    padding: 2px 8px;
}

/* Boutons de Catégories Visuels (Icon Cards) */
QPushButton#catButton {
    background-color: #f3e8ff;
    border: 1px solid #d8b4fe;
    border-radius: 6px;
    color: #581c87;
    font-size: 10.5px;
    font-weight: 700;
    padding: 3px 4px;
}

QPushButton#btnBrowse, QPushButton#btnFolder, QPushButton#btnLink {
    padding: 5px 8px;
    font-size: 11px;
    font-weight: 700;
}

QPushButton#catButton:hover {
    background-color: #ede9fe;
    border-color: #a855f7;
    color: #4c1d95;
}

QPushButton#catButton:checked {
    background-color: #581c87;
    border: 1px solid #7c3aed;
    color: #ffffff;
}

QPushButton#btnToggleAdv {
    background: transparent;
    border: none;
    color: #7c3aed;
    font-size: 11px;
    font-weight: 700;
    text-align: left;
    padding: 2px 0px;
}

QPushButton#btnToggleAdv:hover {
    color: #581c87;
}

/* Inspecteur Média */
#cardHeaderTitle {
    color: #6b21a8;
    font-weight: 800;
    font-size: 11px;
    letter-spacing: 0.8px;
}

#inspectorBadge {
    background: #f3e8ff;
    color: #581c87;
    border: 1px solid #d8b4fe;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 10px;
    font-weight: 700;
}

#inspectorViewport {
    background-color: #f1f5f9;
    border: 1px solid #cbd5e1;
    border-radius: 10px;
}

/* Barre de Contrôle du Lecteur Média Intégré (Aperçu) */
#playerControlBar {
    background-color: #f8fafc;
    border-top: 1px solid #e2e8f0;
    border-bottom-left-radius: 9px;
    border-bottom-right-radius: 9px;
    padding: 3px 6px;
}

QPushButton#btnPlayerCtrl {
    background-color: #f3e8ff;
    border: 1px solid #d8b4fe;
    border-radius: 5px;
    color: #6b21a8;
    font-size: 11px;
    font-weight: 800;
    padding: 0px;
}

QPushButton#btnPlayerCtrl:hover {
    background-color: #ede9fe;
    border-color: #a855f7;
    color: #581c87;
}

QPushButton#btnPlayerFS {
    background-color: #ede9fe;
    border: 1px solid #7c3aed;
    border-radius: 5px;
    color: #581c87;
    font-size: 12px;
    font-weight: 800;
    padding: 0px;
}

QPushButton#btnPlayerFS:hover {
    background-color: #7c3aed;
    color: #ffffff;
}

QLabel#playerTimeLabel {
    color: #475569;
    font-size: 10px;
    font-weight: 700;
    font-family: Consolas, monospace;
}

QSlider#playerTimeSlider::groove:horizontal {
    height: 4px;
    background: #e2e8f0;
    border-radius: 2px;
}

QSlider#playerTimeSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7c3aed, stop:1 #3b82f6);
    border-radius: 2px;
}

QSlider#playerTimeSlider::handle:horizontal {
    background: #6b21a8;
    border: 1px solid #ffffff;
    width: 10px;
    margin-top: -3px;
    margin-bottom: -3px;
    border-radius: 5px;
}

QSlider#playerVolSlider::groove:horizontal {
    height: 4px;
    background: #e2e8f0;
    border-radius: 2px;
}

QSlider#playerVolSlider::sub-page:horizontal {
    background: #7c3aed;
    border-radius: 2px;
}

QSlider#playerVolSlider::handle:horizontal {
    background: #581c87;
    width: 8px;
    margin-top: -2px;
    margin-bottom: -2px;
    border-radius: 4px;
}

#inspectorFilename {
    color: #0f172a;
    font-weight: 700;
    font-size: 13px;
}

#metaLabel {
    color: #64748b;
    font-size: 11px;
    font-weight: 600;
}

#metaVal {
    color: #0f172a;
    font-weight: 700;
    font-size: 11px;
}

/* Destination Label */
#destLabel {
    color: #0f172a;
    font-weight: 700;
    font-size: 12px;
}

/* Tous les Boutons : Arrière-plan Mauve Foncé & Texte Blanc */
QPushButton {
    background-color: #581c87;
    color: #ffffff;
    border: 1px solid #7c3aed;
    border-radius: 8px;
    padding: 7px 16px;
    font-weight: 700;
}

QPushButton:hover {
    background-color: #6b21a8;
    border-color: #a855f7;
    color: #ffffff;
}

QPushButton:pressed {
    background-color: #3b0764;
}

/* Bouton Primaire Immanquable : Mauve Vibrant & Bordure */
QPushButton#btnPrimary {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #7c3aed, stop:1 #581c87);
    border: 1px solid #6b21a8;
    color: #ffffff;
    font-size: 13px;
    font-weight: 900;
    letter-spacing: 0.5px;
    padding: 9px 24px;
}

QPushButton#btnPrimary:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #8b5cf6, stop:1 #6b21a8);
    border: 1px solid #7c3aed;
}

/* Bouton Officiel GRAN LAKU : Mauve Foncé Pur + Texte Blanc */
QPushButton#btnGranLaku {
    background-color: #581c87;
    border: 1px solid #7c3aed;
    color: #ffffff;
    font-weight: 800;
    letter-spacing: 0.5px;
    border-radius: 8px;
    padding: 7px 18px;
}

QPushButton#btnGranLaku:hover {
    background-color: #6b21a8;
    border-color: #a855f7;
    color: #ffffff;
}

/* Bouton Bascule Thème Clair / Sombre */
QPushButton#btnThemeToggle {
    background-color: #f3e8ff;
    border: 1px solid #c084fc;
    color: #581c87;
    font-weight: 800;
    border-radius: 8px;
    padding: 6px 14px;
}

QPushButton#btnThemeToggle:hover {
    background-color: #ede9fe;
    border-color: #7c3aed;
}

/* Sélecteur de Langue 8 Langues (En-tête) */
QComboBox#cbLang {
    background-color: #f3e8ff;
    border: 1px solid #c084fc;
    color: #581c87;
    font-weight: 800;
    border-radius: 8px;
    padding: 5px 10px;
    min-width: 135px;
}

QComboBox#cbLang:hover {
    background-color: #ede9fe;
    border-color: #7c3aed;
}

QComboBox#cbLang QAbstractItemView {
    background-color: #ffffff;
    border: 1px solid #7c3aed;
    color: #0f172a;
    selection-background-color: #f3e8ff;
    selection-color: #581c87;
    font-weight: 700;
}

/* Bouton Individuel de Conversion sur chaque barre de fichier */
QPushButton#btnConvertSingle {
    background-color: #6b21a8;
    border: 1px solid #7c3aed;
    color: #ffffff;
    font-weight: 800;
    border-radius: 6px;
    padding: 2px;
}

QPushButton#btnConvertSingle:hover {
    background-color: #7c3aed;
    border-color: #a855f7;
}

QPushButton#btnTableAction {
    background-color: #f5f3ff;
    border: 1px solid #ddd6fe;
    border-radius: 5px;
    color: #6b21a8;
    font-size: 12px;
    padding: 0px;
}

QPushButton#btnTableAction:hover {
    background-color: #ede9fe;
    border-color: #a855f7;
    color: #581c87;
}

/* Bouton Danger */
QPushButton#btnDanger {
    background-color: #fee2e2;
    border: 1px solid #f87171;
    color: #991b1b;
    font-weight: 700;
    font-size: 12px;
    padding: 0px;
}

QPushButton#btnDanger:hover {
    background-color: #fecaca;
    border-color: #ef4444;
}

/* Bouton & Panneau flottant des Réglages Avancés (Étape 2) */
QPushButton#btnAdvToggle {
    background: transparent;
    border: none;
    color: #6d28d9;
    font-size: 11px;
    font-weight: 800;
    text-align: left;
    padding: 2px 0px;
}

QPushButton#btnAdvToggle:hover {
    color: #4c1d95;
    text-decoration: underline;
}

QFrame#advPopup {
    background-color: #ffffff;
    border: 1px solid #a855f7;
    border-radius: 10px;
}

QLabel#advPopupTitle {
    color: #4c1d95;
    font-size: 12px;
    font-weight: 800;
    padding-bottom: 4px;
    border-bottom: 1px solid #ede9fe;
}

QLabel#advPopupLabel {
    color: #0f172a;
    font-size: 11px;
    font-weight: 700;
}

QLabel#advPopupHint {
    color: #64748b;
    font-size: 10px;
    font-weight: 600;
}

QCheckBox#advPopupCheck {
    spacing: 8px;
    color: #0f172a;
    font-size: 11px;
}

/* Menus Déroulants & Champs */
QComboBox, QSpinBox, QLineEdit {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 6px 10px;
    color: #0f172a;
    font-weight: 600;
}

QComboBox:hover, QSpinBox:hover, QLineEdit:hover {
    border-color: #7c3aed;
}

QComboBox:focus, QSpinBox:focus, QLineEdit:focus {
    border: 1px solid #6b21a8;
    background-color: #faf5ff;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    border: 1px solid #7c3aed;
    selection-background-color: #f3e8ff;
    selection-color: #581c87;
    color: #0f172a;
    padding: 4px;
}

/* Tableau Blanc Pur avec Lignes Douces et En-tête Lavande */
QTableWidget {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    gridline-color: #f1f5f9;
    selection-background-color: #ede9fe;
    selection-color: #4c1d95;
    color: #0f172a;
}

QTableWidget::item {
    padding: 5px 3px;
    border-bottom: 1px solid #f1f5f9;
    color: #0f172a;
}

QHeaderView::section {
    background-color: #f3e8ff;
    color: #4c1d95;
    font-weight: 800;
    font-size: 10.5px;
    padding: 5px 2px;
    border: none;
    border-bottom: 2px solid #7c3aed;
    text-align: center;
}

QPushButton#btnInspect, QPushButton#btnOpenFolder {
    padding: 6px 8px;
    font-size: 11px;
    font-weight: 700;
}

/* Barre de Progression Cyber : Fond Blanc Cassé & Remplissage Mauve */
QProgressBar {
    background-color: #e2e8f0;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    text-align: center;
    color: #0f172a;
    font-weight: 800;
    font-size: 11px;
}

QProgressBar#tableProgressBar {
    background: transparent;
    border: none;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7c3aed, stop:0.5 #8b5cf6, stop:1 #a855f7);
    border-radius: 5px;
}

/* Cases à Cocher Cyber (Ti kare devan chak fichye) */
QCheckBox {
    spacing: 0px;
    color: #0f172a;
    font-weight: 600;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 2px solid #7c3aed;
    background: #ffffff;
}

QCheckBox::indicator:hover {
    border-color: #581c87;
    background: #faf5ff;
}

QCheckBox::indicator:checked {
    background-color: #7c3aed;
    border-color: #581c87;
    image: url(src/ui/icons/check.svg);
}

/* Bouton individuel de conversion animable */
QPushButton#btnConvertSingle {
    background-color: #f3e8ff;
    border: 1px solid #c084fc;
    border-radius: 5px;
    color: #581c87;
    font-size: 12px;
}

QPushButton#btnConvertSingle:hover {
    background-color: #7c3aed;
    border-color: #581c87;
    color: #ffffff;
}

/* Panneau Inférieur & Barre de Processus Futuriste (Mauve & Bleu Fondus) */
#bottomProcessPanel {
    background-color: #ffffff;
    border: 1px solid rgba(124, 58, 237, 0.25);
    border-radius: 10px;
    margin: 4px 0px 8px 0px;
}

#processDetailLabel {
    color: #0f172a;
    font-size: 11px;
    font-weight: 700;
}

#processTimeLabel {
    color: #0284c7;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.3px;
}

QProgressBar#bottomProcessBar {
    background-color: #f1f5f9;
    border: 1px solid rgba(124, 58, 237, 0.3);
    border-radius: 10px;
    text-align: center;
    color: #0f172a;
    font-size: 11px;
    font-weight: 800;
    height: 20px;
}

QProgressBar#bottomProcessBar::chunk {
    background: qlineargradient(
        spread: pad,
        x1: 0, y1: 0, x2: 1, y2: 0,
        stop: 0.0 #6b21a8,
        stop: 0.28 #7c3aed,
        stop: 0.6 #3b82f6,
        stop: 1.0 #0284c7
    );
    border-radius: 9px;
}

/* Barre d'État Inférieure */
QStatusBar {
    background: #ffffff;
    border-top: 1px solid #e2e8f0;
    color: #475569;
    font-size: 12px;
}

QPushButton#versionBadge {
    background: #f3e8ff;
    color: #581c87;
    border: 1px solid #d8b4fe;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 800;
    padding: 3px 10px;
    margin: 2px 8px 2px 0px;
}

QPushButton#versionBadge:hover {
    background: #ede9fe;
    border-color: #a855f7;
    color: #4c1d95;
}

/* Ascenseurs Déroulants (ScrollBars) */
QScrollBar:vertical {
    border: none;
    background: #f8fafc;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: #cbd5e1;
    min-height: 24px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #a855f7;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""

# ==============================================================================
# THÈME SOMBRE STUDIO (DARK THEME)
# Palette : Interface Noir Foncé, Boutons Mauve Foncé, Accents Mauve
# ==============================================================================
DARK_THEME_STYLE = """
QMainWindow {
    background-color: #050507;
}

QWidget {
    color: #f8fafc;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    font-size: 13px;
}

#headerFrame {
    background: #0d0c14;
    border-bottom: 2px solid #7c3aed;
    padding: 10px 20px;
}

QLabel#headerStudioBadge {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7c3aed, stop:1 #a855f7);
    color: #ffffff;
    font-size: 10px;
    font-weight: 800;
    padding: 3px 8px;
    border-radius: 6px;
    letter-spacing: 1px;
}

#headerTitle {
    color: #ffffff;
    font-size: 22px;
    font-weight: 900;
    letter-spacing: 0.8px;
}

#headerSubtitle {
    color: #d8b4fe;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.4px;
}

#cardFrame, #presetPanel, #mediaPreviewCard, QGroupBox {
    background-color: rgba(13, 13, 16, 0.92);
    border: 1px solid rgba(139, 92, 246, 0.35);
    border-radius: 12px;
    padding: 0px;
}

#dropZone {
    background-color: rgba(13, 11, 20, 0.92);
    border: 2px dashed rgba(168, 85, 247, 0.6);
    border-radius: 12px;
    padding: 0px;
}

#dropZone[dragActive="true"] {
    border: 2px dashed #c084fc;
    background-color: rgba(45, 16, 75, 0.95);
}

#dropTitle {
    font-size: 17px;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: 0.4px;
}

#dropSub {
    font-size: 12px;
    color: #d8b4fe;
    font-weight: 600;
    letter-spacing: 0.3px;
}

QLabel#stepBadge, .stepBadge {
    color: #d8b4fe;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.8px;
    background: rgba(88, 28, 135, 0.4);
    border: 1px solid rgba(168, 85, 247, 0.4);
    border-radius: 4px;
    padding: 2px 8px;
}

QPushButton#catButton {
    background-color: #200a33;
    border: 1px solid rgba(139, 92, 246, 0.4);
    border-radius: 6px;
    color: #ffffff;
    font-size: 10.5px;
    font-weight: 700;
    padding: 3px 4px;
}

QPushButton#btnBrowse, QPushButton#btnFolder, QPushButton#btnLink {
    padding: 5px 8px;
    font-size: 11px;
    font-weight: 700;
}

QPushButton#catButton:hover {
    background-color: #351054;
    border-color: #c084fc;
    color: #ffffff;
}

QPushButton#catButton:checked {
    background-color: #4c1d95;
    border: 1px solid #c084fc;
    color: #ffffff;
}

QPushButton#btnToggleAdv {
    background: transparent;
    border: none;
    color: #a855f7;
    font-size: 11px;
    font-weight: 700;
    text-align: left;
    padding: 2px 0px;
}

QPushButton#btnToggleAdv:hover {
    color: #d8b4fe;
}

#cardHeaderTitle {
    color: #d8b4fe;
    font-weight: 800;
    font-size: 11px;
    letter-spacing: 0.8px;
}

#inspectorBadge {
    background: #230c38;
    color: #c084fc;
    border: 1px solid #7c3aed;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 10px;
    font-weight: 700;
}

#inspectorViewport {
    background-color: #070709;
    border: 1px solid rgba(139, 92, 246, 0.25);
    border-radius: 10px;
}

/* Barre de Contrôle du Lecteur Média Intégré (Aperçu) */
#playerControlBar {
    background-color: rgba(9, 9, 13, 0.95);
    border-top: 1px solid rgba(139, 92, 246, 0.3);
    border-bottom-left-radius: 9px;
    border-bottom-right-radius: 9px;
    padding: 3px 6px;
}

QPushButton#btnPlayerCtrl {
    background-color: #1a162b;
    border: 1px solid #4c1d95;
    border-radius: 5px;
    color: #e9d5ff;
    font-size: 11px;
    font-weight: 800;
    padding: 0px;
}

QPushButton#btnPlayerCtrl:hover {
    background-color: #3b125f;
    border-color: #a855f7;
    color: #ffffff;
}

QPushButton#btnPlayerFS {
    background-color: #2e1065;
    border: 1px solid #a855f7;
    border-radius: 5px;
    color: #f3e8ff;
    font-size: 12px;
    font-weight: 800;
    padding: 0px;
}

QPushButton#btnPlayerFS:hover {
    background-color: #7c3aed;
    border-color: #c084fc;
    color: #ffffff;
}

QLabel#playerTimeLabel {
    color: #c4b5fd;
    font-size: 10px;
    font-weight: 700;
    font-family: Consolas, monospace;
}

QSlider#playerTimeSlider::groove:horizontal {
    height: 4px;
    background: #1e1b4b;
    border-radius: 2px;
}

QSlider#playerTimeSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8b5cf6, stop:1 #38bdf8);
    border-radius: 2px;
}

QSlider#playerTimeSlider::handle:horizontal {
    background: #ffffff;
    border: 1px solid #c084fc;
    width: 10px;
    margin-top: -3px;
    margin-bottom: -3px;
    border-radius: 5px;
}

QSlider#playerVolSlider::groove:horizontal {
    height: 4px;
    background: #1e1b4b;
    border-radius: 2px;
}

QSlider#playerVolSlider::sub-page:horizontal {
    background: #a855f7;
    border-radius: 2px;
}

QSlider#playerVolSlider::handle:horizontal {
    background: #ffffff;
    width: 8px;
    margin-top: -2px;
    margin-bottom: -2px;
    border-radius: 4px;
}

#inspectorFilename {
    color: #ffffff;
    font-weight: 700;
    font-size: 13px;
}

#metaLabel {
    color: #c4b5fd;
    font-size: 11px;
    font-weight: 600;
}

#metaVal {
    color: #ffffff;
    font-weight: 700;
    font-size: 11px;
}

#destLabel {
    color: #ffffff;
    font-weight: 700;
    font-size: 12px;
}

QPushButton {
    background-color: #2a0f44;
    color: #ffffff;
    border: 1px solid rgba(139, 92, 246, 0.55);
    border-radius: 8px;
    padding: 7px 16px;
    font-weight: 700;
}

QPushButton:hover {
    background-color: #3f1566;
    border-color: #c084fc;
    color: #ffffff;
}

QPushButton:pressed {
    background-color: #1c082e;
}

QPushButton#btnPrimary {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4c1d95, stop:1 #350c5a);
    border: 1px solid #a855f7;
    color: #ffffff;
    font-size: 13px;
    font-weight: 900;
    letter-spacing: 0.5px;
    padding: 9px 24px;
}

QPushButton#btnPrimary:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #5b21b6, stop:1 #431070);
    border: 1px solid #c084fc;
}

QPushButton#btnGranLaku {
    background-color: #260c3d;
    border: 1px solid #7c3aed;
    color: #ffffff;
    font-weight: 800;
    letter-spacing: 0.5px;
    border-radius: 8px;
    padding: 7px 18px;
}

QPushButton#btnGranLaku:hover {
    background-color: #3d125f;
    border-color: #c084fc;
    color: #ffffff;
}

QPushButton#btnThemeToggle {
    background-color: #2a0f44;
    border: 1px solid #7c3aed;
    color: #ffffff;
    font-weight: 800;
    border-radius: 8px;
    padding: 6px 14px;
}

QPushButton#btnThemeToggle:hover {
    background-color: #3f1566;
    border-color: #c084fc;
}

/* Sélecteur de Langue 8 Langues (En-tête) */
QComboBox#cbLang {
    background-color: #2a0f44;
    border: 1px solid #7c3aed;
    color: #ffffff;
    font-weight: 800;
    border-radius: 8px;
    padding: 5px 10px;
    min-width: 135px;
}

QComboBox#cbLang:hover {
    background-color: #3f1566;
    border-color: #c084fc;
}

QComboBox#cbLang QAbstractItemView {
    background-color: #161026;
    border: 1px solid #a855f7;
    color: #f8fafc;
    selection-background-color: #3b125f;
    selection-color: #e9d5ff;
    font-weight: 700;
}

QPushButton#btnConvertSingle {
    background-color: #3b125f;
    border: 1px solid #a855f7;
    color: #ffffff;
    font-weight: 800;
    border-radius: 6px;
    padding: 2px;
}

QPushButton#btnConvertSingle:hover {
    background-color: #5b21b6;
    border-color: #e879f9;
}

QPushButton#btnTableAction {
    background-color: #1a162b;
    border: 1px solid #4c1d95;
    border-radius: 5px;
    color: #e9d5ff;
    font-size: 12px;
    padding: 0px;
}

QPushButton#btnTableAction:hover {
    background-color: #3b125f;
    border-color: #a855f7;
    color: #ffffff;
}

QPushButton#btnDanger {
    background-color: #3b0d19;
    border: 1px solid #991b1b;
    color: #fecaca;
    font-weight: 700;
    font-size: 12px;
    padding: 0px;
}

QPushButton#btnDanger:hover {
    background-color: #551224;
    border-color: #ef4444;
}

/* Bouton & Panneau flottant des Réglages Avancés (Étape 2) */
QPushButton#btnAdvToggle {
    background: transparent;
    border: none;
    color: #c084fc;
    font-size: 11px;
    font-weight: 800;
    text-align: left;
    padding: 2px 0px;
}

QPushButton#btnAdvToggle:hover {
    color: #e9d5ff;
    text-decoration: underline;
}

QFrame#advPopup {
    background-color: #14121c;
    border: 1px solid #a855f7;
    border-radius: 10px;
}

QLabel#advPopupTitle {
    color: #e9d5ff;
    font-size: 12px;
    font-weight: 800;
    padding-bottom: 4px;
    border-bottom: 1px solid rgba(168, 85, 247, 0.35);
}

QLabel#advPopupLabel {
    color: #f1f5f9;
    font-size: 11px;
    font-weight: 700;
}

QLabel#advPopupHint {
    color: #a1a1aa;
    font-size: 10px;
    font-weight: 600;
}

QCheckBox#advPopupCheck {
    spacing: 8px;
    color: #f1f5f9;
    font-size: 11px;
}

QComboBox, QSpinBox, QLineEdit {
    background-color: #111116;
    border: 1px solid rgba(139, 92, 246, 0.38);
    border-radius: 6px;
    padding: 6px 10px;
    color: #ffffff;
    font-weight: 600;
}

QComboBox:hover, QSpinBox:hover, QLineEdit:hover {
    border-color: #a855f7;
}

QComboBox:focus, QSpinBox:focus, QLineEdit:focus {
    border: 1px solid #c084fc;
    background-color: #16161e;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #0f0f14;
    border: 1px solid #7c3aed;
    selection-background-color: #3b0764;
    selection-color: #ffffff;
    color: #e9d5ff;
    padding: 4px;
}

QTableWidget {
    background-color: rgba(11, 11, 14, 0.92);
    border: 1px solid rgba(139, 92, 246, 0.3);
    border-radius: 12px;
    gridline-color: rgba(124, 58, 237, 0.18);
    selection-background-color: rgba(76, 29, 149, 0.6);
    selection-color: #ffffff;
    color: #f8fafc;
}

QTableWidget::item {
    padding: 5px 3px;
    border-bottom: 1px solid rgba(124, 58, 237, 0.15);
    color: #f8fafc;
}

QHeaderView::section {
    background-color: #101015;
    color: #d8b4fe;
    font-weight: 700;
    font-size: 10.5px;
    padding: 5px 2px;
    border: none;
    border-bottom: 2px solid #7c3aed;
    text-align: center;
}

QPushButton#btnInspect, QPushButton#btnOpenFolder {
    padding: 6px 8px;
    font-size: 11px;
    font-weight: 700;
}

QProgressBar {
    background-color: #0b0b0e;
    border: 1px solid rgba(139, 92, 246, 0.35);
    border-radius: 6px;
    text-align: center;
    color: #ffffff;
    font-weight: 800;
    font-size: 11px;
}

QProgressBar#tableProgressBar {
    background: transparent;
    border: none;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6b21a8, stop:0.5 #8b5cf6, stop:1 #c084fc);
    border-radius: 5px;
}

QCheckBox {
    spacing: 0px;
    color: #f8fafc;
    font-weight: 600;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 2px solid #a855f7;
    background: #111116;
}

QCheckBox::indicator:hover {
    border-color: #c084fc;
    background: #230c38;
}

QCheckBox::indicator:checked {
    background-color: #7c3aed;
    border-color: #c084fc;
    image: url(src/ui/icons/check.svg);
}

/* Bouton individuel de conversion animable */
QPushButton#btnConvertSingle {
    background-color: #2a0f44;
    border: 1px solid #7c3aed;
    border-radius: 5px;
    color: #ffffff;
    font-size: 12px;
}

QPushButton#btnConvertSingle:hover {
    background-color: #4c1d95;
    border-color: #c084fc;
}

QPushButton#btnTableAction {
    background-color: #1a162b;
    border: 1px solid #4c1d95;
    border-radius: 5px;
    color: #e9d5ff;
    font-size: 12px;
    padding: 0px;
}

QPushButton#btnTableAction:hover {
    background-color: #3b125f;
    border-color: #a855f7;
    color: #ffffff;
}

/* Panneau Inférieur & Barre de Processus Futuriste (Mauve & Bleu Fondus) */
#bottomProcessPanel {
    background-color: #08080c;
    border: 1px solid rgba(139, 92, 246, 0.3);
    border-radius: 10px;
    margin: 4px 0px 8px 0px;
}

#processDetailLabel {
    color: #e2e8f0;
    font-size: 11px;
    font-weight: 700;
}

#processTimeLabel {
    color: #38bdf8;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.3px;
}

QProgressBar#bottomProcessBar {
    background-color: #0f0e17;
    border: 1px solid rgba(139, 92, 246, 0.4);
    border-radius: 10px;
    text-align: center;
    color: #ffffff;
    font-size: 11px;
    font-weight: 800;
    height: 20px;
}

QProgressBar#bottomProcessBar::chunk {
    background: qlineargradient(
        spread: pad,
        x1: 0, y1: 0, x2: 1, y2: 0,
        stop: 0.0 #581c87,
        stop: 0.25 #7c3aed,
        stop: 0.55 #8b5cf6,
        stop: 0.8 #2563eb,
        stop: 1.0 #06b6d4
    );
    border-radius: 9px;
}

QStatusBar {
    background: #070709;
    border-top: 1px solid rgba(124, 58, 237, 0.28);
    color: #c4b5fd;
    font-size: 12px;
}

QPushButton#versionBadge {
    background: #1b0a2a;
    color: #e9d5ff;
    border: 1px solid rgba(168, 85, 247, 0.6);
    border-radius: 6px;
    font-size: 11px;
    font-weight: 800;
    padding: 3px 10px;
    margin: 2px 8px 2px 0px;
}

QPushButton#versionBadge:hover {
    background: #31104e;
    border-color: #c084fc;
    color: #ffffff;
}

QScrollBar:vertical {
    border: none;
    background: #070709;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: rgba(139, 92, 246, 0.45);
    min-height: 24px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #a855f7;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""

# Par défaut, toute l'application démarre en THÈME SOMBRE STUDIO (reposant pour les yeux)
STUDIO_STYLE = DARK_THEME_STYLE

def get_theme_stylesheet(is_light: bool = False) -> str:
    """Retourne la feuille de style QSS correspondant au thème choisi (sombre par défaut)."""
    return LIGHT_THEME_STYLE if is_light else DARK_THEME_STYLE

"""
Capture d'écran et validation visuelle : Bouton et Dialogue de Lien Local
"""
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QApplication

from src.ui.main_window import MainWindow
from src.ui.link_input_dialog import LocalLinkDialog

def main():
    app = QApplication.instance() or QApplication(sys.argv)
    output_dir = Path("tests/screenshots")
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Capture MainWindow avec les 3 boutons dans l'Étape 1 (Thème Clair)
    win_light = MainWindow(is_light_mode=True)
    win_light.resize(1200, 750)
    win_light.show()
    app.processEvents()

    # Ajouter un lien de test local
    win_light._on_files_added(["http://localhost:3000/animation-studio"])
    app.processEvents()

    win_light.grab().save(str(output_dir / "step1_local_link_added_light.png"))

    # 2. Capture MainWindow en Kreyòl Ayisyen
    from src.core.i18n import I18nManager
    I18nManager.get_instance().set_language("ht")
    app.processEvents()
    win_light.grab().save(str(output_dir / "step1_local_link_added_kreyol.png"))

    # 3. Capture du dialogue LocalLinkDialog
    dlg = LocalLinkDialog(win_light)
    dlg.show()
    app.processEvents()
    dlg.grab().save(str(output_dir / "dialog_local_link_preview.png"))
    dlg.close()

    win_light.close()
    print("Captures générées avec succès dans tests/screenshots/")

if __name__ == "__main__":
    main()

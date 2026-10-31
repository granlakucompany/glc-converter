"""
Capture d'écrans multi-langues pour vérification visuelle dans WASDEV.
"""
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from src.ui.main_window import MainWindow
from src.core.i18n import I18nManager

def capture_screenshots():
    app = QApplication.instance() or QApplication(sys.argv)
    
    win = MainWindow(is_light_mode=False)
    win.show()
    win.resize(1280, 800)
    
    output_dir = project_root / "tests" / "screenshots"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    i18n = I18nManager.get_instance()
    
    # 1. Capture en Kreyòl Ayisyen
    i18n.set_language("ht")
    app.processEvents()
    pix_ht = win.grab()
    path_ht = output_dir / "glc_converter_kreyol_ht.png"
    pix_ht.save(str(path_ht))
    print(f"Captured: {path_ht}")
    
    # 2. Capture en Français
    i18n.set_language("fr")
    app.processEvents()
    pix_fr = win.grab()
    path_fr = output_dir / "glc_converter_francais_fr.png"
    pix_fr.save(str(path_fr))
    print(f"Captured: {path_fr}")
    
    # 3. Capture en English
    i18n.set_language("en")
    app.processEvents()
    pix_en = win.grab()
    path_en = output_dir / "glc_converter_english_en.png"
    pix_en.save(str(path_en))
    print(f"Captured: {path_en}")

    win.close()
    if hasattr(win, "telemetry_timer"):
        win.telemetry_timer.stop()
    print("Done capturing screenshots.")
    import os
    os._exit(0)

if __name__ == "__main__":
    capture_screenshots()

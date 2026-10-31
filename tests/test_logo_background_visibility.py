"""
Validation visuelle haute résolution du Header, du Logo officiel agrandi,
de la typographie vectorielle nette, de la description et du fond cybernétique rehaussé.
"""
import sys
import os
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PySide6.QtWidgets import QApplication
from src.core.converter_engine import ConversionTask
from src.ui.main_window import MainWindow
from src.ui.theme import get_theme_stylesheet

def run_test():
    app = QApplication.instance() or QApplication(sys.argv)
    app.setStyleSheet(get_theme_stylesheet(False))

    window = MainWindow(is_light_mode=False)
    window.telemetry_timer.stop()
    window.cyber_bg.timer.stop()
    window.resize(1300, 860)

    sample_path = os.path.abspath("composition.html")
    if not os.path.exists(sample_path):
        sample_path = os.path.abspath("tests/test_logo_background_visibility.py")

    task = ConversionTask(
        task_id="test_visual_02",
        input_path=sample_path,
        output_format="mp4",
        output_dir="OUTPUT",
        file_info={"size_formatted": "172.4 KB", "extension": "HTML"}
    )
    window.tasks.append(task)
    window.task_table.add_task(task)

    window.show()
    app.processEvents()

    os.makedirs("tests/screenshots", exist_ok=True)
    
    # 1. Capture Dark Mode
    out_dark = os.path.abspath("tests/screenshots/verified_header_and_bg_dark.png")
    pix_dark = window.grab()
    pix_dark.save(out_dark)
    print(f"-> Full dark window saved : {out_dark}")

    # Crop Header & Drop Zone
    crop_header = pix_dark.copy(0, 0, 1300, 420)
    crop_path = os.path.abspath("tests/screenshots/crop_header_and_dropzone.png")
    crop_header.save(crop_path)
    print(f"-> Crop header & dropzone saved : {crop_path}")

    # 2. Capture Light Mode
    window._toggle_theme()
    app.processEvents()
    out_light = os.path.abspath("tests/screenshots/verified_header_and_bg_light.png")
    window.grab().save(out_light)
    print(f"-> Full light window saved : {out_light}")

    window.close()
    print("-> VALIDATION VISUELLE TERMINÉE AVEC SUCCÈS !")

if __name__ == "__main__":
    run_test()

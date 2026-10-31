"""
Capture visuelle du volet « Réglages Avancés » (Étape 2) en thème clair et sombre.
Usage : python tests/capture_advanced_panel.py <suffixe>
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PySide6.QtCore import Qt, QCoreApplication
from PySide6.QtWidgets import QApplication

QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts, True)
app = QApplication.instance() or QApplication(sys.argv)

from src.ui.theme import get_theme_stylesheet
from src.ui.main_window import MainWindow

OUT = Path(__file__).resolve().parent / "screenshots"
OUT.mkdir(exist_ok=True)
suffix = sys.argv[1] if len(sys.argv) > 1 else "after"


def pump(sec=0.4):
    t = time.time()
    while time.time() - t < sec:
        app.processEvents()


for light in (True, False):
    app.setStyleSheet(get_theme_stylesheet(light))
    win = MainWindow(is_light_mode=light)
    win.resize(1300, 860)
    win.show()
    pump(1.0)

    panel = win.preset_panel
    panel.btn_toggle_adv.click()
    pump(0.6)

    name = "light" if light else "dark"
    win.grab().save(str(OUT / f"advanced_{suffix}_{name}_window.png"))
    popup = getattr(panel, "adv_popup", None)
    if popup is not None and popup.isVisible():
        popup.grab().save(str(OUT / f"advanced_{suffix}_{name}_popup.png"))
    print(name, "adv visible:", panel.adv_container.isVisible(),
          "adv height:", panel.adv_container.height(),
          "button text:", panel.btn_toggle_adv.text(),
          "button width:", panel.btn_toggle_adv.width(),
          "text width needed:", panel.btn_toggle_adv.fontMetrics().horizontalAdvance(panel.btn_toggle_adv.text()))
    panel.adv_popup.hide()
    pump(0.2)

    card = win.preview_card
    for w, h in ((1300, 860), (960, 600)):
        win.resize(w, h)
        pump(0.5)
        card.grab().save(str(OUT / f"inspector_{suffix}_{name}_{w}x{h}.png"))
        lbl = card.lbl_time
        print(name, f"{w}x{h}", "time label:", repr(lbl.text()), "width:", lbl.width(),
              "needed:", lbl.fontMetrics().horizontalAdvance(lbl.text()),
              "badge height:", card.lbl_badge_category.height())
    win.close()
    pump(0.3)

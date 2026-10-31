"""
Non-régression : panneau « Réglages Avancés », boutons du lecteur de l'inspecteur
et bouton « Vider », avec la feuille de style réelle appliquée (thème clair et sombre).
Les défauts corrigés n'apparaissaient qu'avec le QSS : il est donc appliqué ici.
"""
import sys
import time
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PySide6.QtWidgets import QApplication

app = QApplication.instance() or QApplication(sys.argv)

from src.ui.theme import get_theme_stylesheet
from src.ui.main_window import MainWindow


def pump(sec=0.3):
    t = time.time()
    while time.time() - t < sec:
        app.processEvents()


class TestAdvancedAndPlayerButtons(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._old_qss = app.styleSheet()

    @classmethod
    def tearDownClass(cls):
        app.setStyleSheet(cls._old_qss)
        pump(0.1)

    def _open_window(self, light: bool, size=(1300, 860)):
        app.setStyleSheet(get_theme_stylesheet(light))
        win = MainWindow(is_light_mode=light)
        win.resize(*size)
        win.show()
        win.activateWindow()
        pump(0.8)
        self.addCleanup(lambda: (win.close(), pump(0.1)))
        return win

    def test_advanced_popup_opens_with_readable_content(self):
        for light in (True, False):
            with self.subTest(theme="clair" if light else "sombre"):
                win = self._open_window(light)
                panel = win.preset_panel
                btn = panel.btn_toggle_adv
                # Le texte complet du bouton tient dans sa largeur
                self.assertGreaterEqual(btn.width(), btn.fontMetrics().horizontalAdvance(btn.text()))

                btn.click()
                pump(0.4)
                self.assertTrue(panel.adv_popup.isVisible(), "le panneau avancé ne s'ouvre pas")
                for w in (panel.lbl_adv_title, panel.cb_resolution, panel.sp_crf, panel.chk_hw_accel):
                    self.assertTrue(w.isVisible())
                    self.assertGreater(w.height(), 10)
                self.assertGreaterEqual(panel.cb_resolution.height(), 32)
                self.assertTrue(panel.lbl_adv_title.text())

                btn.click()
                pump(0.3)
                self.assertFalse(panel.adv_popup.isVisible())

    def test_player_buttons_keep_their_size(self):
        for light in (True, False):
            for size in ((1300, 860), (960, 600)):
                with self.subTest(theme="clair" if light else "sombre", size=size):
                    win = self._open_window(light, size)
                    card = win.preview_card
                    self.assertEqual(card.btn_play.size().width(), 26)
                    self.assertEqual(card.btn_play.size().height(), 26)
                    self.assertEqual(card.btn_mute.size().width(), 24)
                    self.assertEqual(card.btn_mute.size().height(), 24)
                    self.assertEqual(card.btn_fullscreen.size().width(), 26)
                    self.assertEqual(card.btn_fullscreen.size().height(), 26)
                    lbl = card.lbl_time
                    self.assertGreaterEqual(lbl.width(), lbl.fontMetrics().horizontalAdvance(lbl.text()))

    def test_clear_and_html_buttons_same_height(self):
        for light in (True, False):
            with self.subTest(theme="clair" if light else "sombre"):
                win = self._open_window(light)
                self.assertEqual(win.btn_clear.height(), win.btn_html.height())
                self.assertGreaterEqual(win.btn_clear.height(), 30)


if __name__ == "__main__":
    unittest.main()

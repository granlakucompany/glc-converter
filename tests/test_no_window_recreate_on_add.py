"""
Test de non-régression : l'ajout d'un fichier HTML (ou autre média) ne doit pas
détruire puis recréer la fenêtre native principale (effet « le logiciel se ferme
puis réapparaît »).
"""
import sys
import time
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PySide6.QtCore import Qt, QObject, QEvent, QCoreApplication
from PySide6.QtWidgets import QApplication

QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts, True)
app = QApplication.instance() or QApplication(sys.argv)

from src.ui.main_window import MainWindow


class _HideCounter(QObject):
    def __init__(self):
        super().__init__()
        self.hides = 0

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.Hide:
            self.hides += 1
        return False


def _pump(n=30):
    for _ in range(n):
        app.processEvents()


def _wait(predicate, timeout=5.0):
    deadline = time.monotonic() + timeout
    while not predicate() and time.monotonic() < deadline:
        app.processEvents()
        time.sleep(0.01)
    return predicate()


class TestNoWindowRecreateOnAdd(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="glc_recreate_")
        self.html = Path(self.tmp) / "animation.html"
        self.html.write_text(
            "<html><body style='background:#000'><div>GLC</div></body></html>",
            encoding="utf-8",
        )

    def test_web_view_exists_before_show(self):
        win = MainWindow()
        self.assertIsNotNone(win.preview_card.web_view,
                             "Le lecteur Web doit être créé avant l'affichage de la fenêtre")
        win.close()

    def test_adding_html_keeps_same_native_window(self):
        win = MainWindow()
        # Même séquence que main.py : afficher seulement quand le lecteur Web est prêt
        # Premier démarrage de Chromium (QtWebEngine) : plusieurs secondes sur une machine chargée
        self.assertTrue(_wait(lambda: win.preview_card.web_ready, timeout=15.0), "Le lecteur Web n'est jamais prêt")
        win.show()
        _pump()

        win_id_before = int(win.winId())
        counter = _HideCounter()
        win.installEventFilter(counter)

        win._on_files_added([str(self.html)])
        _pump(60)

        self.assertEqual(int(win.winId()), win_id_before,
                         "La fenêtre native a été recréée lors de l'ajout du HTML")
        self.assertEqual(counter.hides, 0, "La fenêtre a été masquée lors de l'ajout du HTML")
        self.assertTrue(win.isVisible())
        self.assertIs(win.preview_card.media_stack.currentWidget(), win.preview_card.web_view)

        win.removeEventFilter(counter)
        win.close()


if __name__ == "__main__":
    unittest.main()

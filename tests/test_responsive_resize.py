import sys
import unittest
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QSize
from src.ui.main_window import MainWindow

app = QApplication.instance() or QApplication(sys.argv)

class TestResponsiveResize(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.win = MainWindow()
        cls.win.show()
        app.processEvents()

    @classmethod
    def tearDownClass(cls):
        cls.win.close()
        app.processEvents()

    def test_minimum_size_configuration(self):
        """Vérifie que la taille minimale de la fenêtre principale est calibrée à 960x600."""
        min_size = self.win.minimumSize()
        self.assertEqual(min_size.width(), 960)
        self.assertEqual(min_size.height(), 600)

    def test_responsive_layout_at_min_size(self):
        """Vérifie qu'à la dimension minimale (960x600), tous les composants restent ajustés et visibles."""
        self.win.resize(960, 600)
        app.processEvents()

        # 1. Vérification de la hauteur du guide didactique (workflow)
        wf = self.win.findChild(MainWindow, "workflowFrame") or getattr(self.win, "drop_zone").parent()
        self.assertGreaterEqual(self.win.drop_zone.height(), 120)
        self.assertGreaterEqual(self.win.preset_panel.height(), 120)

        # 2. Boutons d'ajout de fichiers dans Étape 1
        self.assertTrue(self.win.drop_zone.btn_browse.isVisible())
        self.assertTrue(self.win.drop_zone.btn_folder.isVisible())
        self.assertGreater(self.win.drop_zone.btn_browse.width(), 40)
        self.assertGreater(self.win.drop_zone.btn_folder.width(), 40)

        # 3. Tableau des tâches et toutes ses colonnes
        table = self.win.task_table
        self.assertEqual(table.columnCount(), 9)
        for col in range(table.columnCount()):
            self.assertGreater(table.columnWidth(col), 20, f"Colonne {col} trop étroite")

        # 4. Carte d'inspection
        card = self.win.preview_card
        self.assertGreaterEqual(card.width(), 240)
        self.assertTrue(card.btn_inspect.isVisible())
        self.assertTrue(card.btn_open_folder.isVisible())

    def test_header_adaptive_behavior(self):
        """Vérifie le comportement réactif de l'en-tête (description condensée sous 1120px)."""
        # Sous 1120px : description masquée pour laisser la priorité au titre et boutons
        self.win.resize(960, 600)
        app.processEvents()
        self.assertFalse(self.win.lbl_brand_desc.isVisible())
        self.assertEqual(self.win.btn_web.text(), "🌐 GRAN LAKU")

        # Au-dessus de 1120px : description complète affichée
        self.win.resize(1280, 720)
        app.processEvents()
        self.assertTrue(self.win.lbl_brand_desc.isVisible())

if __name__ == "__main__":
    unittest.main()

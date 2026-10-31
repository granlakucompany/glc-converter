"""
Test d'intégration complet pour la mémorisation automatique et dynamique
du dernier emplacement d'ouverture de fichier dans GLC CONVERTER.
"""
import sys
import os
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PySide6.QtWidgets import QApplication
from src.core.settings_manager import (
    SettingsManager, get_last_open_dir, set_last_open_dir,
    get_output_dir, set_output_dir
)
from src.ui.drop_zone import DropZoneWidget
from src.ui.html_to_video_dialog import HtmlToVideoDialog
from src.ui.main_window import MainWindow

app = QApplication.instance() or QApplication(sys.argv)

class TestRememberLastOpenLocation(unittest.TestCase):
    def setUp(self):
        self.dir_a = tempfile.mkdtemp(prefix="glc_folder_A_")
        self.file_a = Path(self.dir_a) / "media_A.mp4"
        self.file_a.write_text("dummy")

        self.dir_b = tempfile.mkdtemp(prefix="glc_folder_B_")
        self.file_b = Path(self.dir_b) / "animation.html"
        self.file_b.write_text("<html></html>")

    def tearDown(self):
        for f in [self.file_a, self.file_b]:
            try:
                if f.exists():
                    f.unlink()
            except Exception:
                pass
        for d in [self.dir_a, self.dir_b]:
            try:
                if os.path.exists(d):
                    os.rmdir(d)
            except Exception:
                pass

    def test_drop_zone_browse_files_updates_last_dir(self):
        dz = DropZoneWidget()
        
        # Simuler la sélection d'un fichier dans le dossier A
        with patch("PySide6.QtWidgets.QFileDialog.getOpenFileNames") as mock_dialog:
            mock_dialog.return_value = ([str(self.file_a)], "All (*.*)")
            dz._browse_files()
            
            # Vérifier que le dossier A a été enregistré
            self.assertEqual(get_last_open_dir(), str(Path(self.dir_a).resolve()))

        # Lors du prochain appel, QFileDialog DOIT recevoir le dossier A comme point de départ
        with patch("PySide6.QtWidgets.QFileDialog.getOpenFileNames") as mock_dialog_next:
            mock_dialog_next.return_value = ([str(self.file_b)], "All (*.*)")
            dz._browse_files()
            
            # Vérification du dossier de départ transmis au dialogue
            args, _ = mock_dialog_next.call_args
            initial_dir = args[2]
            self.assertEqual(initial_dir, str(Path(self.dir_a).resolve()))
            
            # Et maintenant, le dernier dossier mémorisé DOIT être le dossier B
            self.assertEqual(get_last_open_dir(), str(Path(self.dir_b).resolve()))

    def test_drop_zone_browse_folder_updates_last_dir(self):
        dz = DropZoneWidget()
        with patch("PySide6.QtWidgets.QFileDialog.getExistingDirectory") as mock_dir_dialog:
            mock_dir_dialog.return_value = self.dir_a
            dz._browse_folder()
            self.assertEqual(get_last_open_dir(), str(Path(self.dir_a).resolve()))

    def test_main_window_files_added_remembers_location(self):
        window = MainWindow(is_light_mode=False)
        window.telemetry_timer.stop()
        window.cyber_bg.timer.stop()
        
        # L'utilisateur dépose des fichiers depuis le dossier B
        window._on_files_added([str(self.file_b)])
        self.assertEqual(get_last_open_dir(), str(Path(self.dir_b).resolve()))
        window.close()

    def test_html_to_video_dialog_browse_remembers_location(self):
        # Initialement sur dossier A
        set_last_open_dir(self.dir_a)
        
        dlg = HtmlToVideoDialog()
        with patch("PySide6.QtWidgets.QFileDialog.getOpenFileName") as mock_html_dialog:
            mock_html_dialog.return_value = (str(self.file_b), "HTML (*.html)")
            dlg._browse()
            
            # Le dialogue devait démarrer dans le dossier A
            args, _ = mock_html_dialog.call_args
            self.assertEqual(args[2], str(Path(self.dir_a).resolve()))
            
            # Et mémoriser le nouveau dossier B
            self.assertEqual(get_last_open_dir(), str(Path(self.dir_b).resolve()))

if __name__ == "__main__":
    unittest.main()

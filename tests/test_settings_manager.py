"""
Tests unitaires pour la gestion et la mémorisation de l'emplacement du dernier fichier ouvert
(SettingsManager) dans GLC CONVERTER.
"""
import os
import sys
import unittest
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core.settings_manager import (
    SettingsManager, get_last_open_dir, set_last_open_dir,
    get_output_dir, set_output_dir
)

class TestSettingsManager(unittest.TestCase):
    def setUp(self):
        self.mgr = SettingsManager.get_instance()
        self.temp_dir = tempfile.mkdtemp()
        self.temp_file = Path(self.temp_dir) / "test_media.mp4"
        self.temp_file.write_text("dummy")

    def tearDown(self):
        try:
            if self.temp_file.exists():
                self.temp_file.unlink()
            if os.path.exists(self.temp_dir):
                os.rmdir(self.temp_dir)
        except Exception:
            pass

    def test_default_last_open_dir(self):
        d = get_last_open_dir()
        self.assertTrue(os.path.isdir(d))

    def test_set_last_open_dir_with_file(self):
        res = set_last_open_dir(self.temp_file)
        self.assertEqual(res, str(Path(self.temp_dir).resolve()))
        self.assertEqual(get_last_open_dir(), str(Path(self.temp_dir).resolve()))

    def test_set_last_open_dir_with_directory(self):
        res = set_last_open_dir(self.temp_dir)
        self.assertEqual(res, str(Path(self.temp_dir).resolve()))
        self.assertEqual(get_last_open_dir(), str(Path(self.temp_dir).resolve()))

    def test_update_on_every_open(self):
        # Création d'un deuxième dossier temporaire
        dir2 = tempfile.mkdtemp()
        file2 = Path(dir2) / "anim.html"
        file2.write_text("<html></html>")

        try:
            set_last_open_dir(self.temp_file)
            self.assertEqual(get_last_open_dir(), str(Path(self.temp_dir).resolve()))

            # L'utilisateur ouvre maintenant un fichier ailleurs
            set_last_open_dir(file2)
            self.assertEqual(get_last_open_dir(), str(Path(dir2).resolve()))
        finally:
            if file2.exists():
                file2.unlink()
            if os.path.exists(dir2):
                os.rmdir(dir2)

    def test_persistence_in_new_instance(self):
        set_last_open_dir(self.temp_dir)
        new_mgr = SettingsManager()
        self.assertEqual(new_mgr.get_last_open_dir(), str(Path(self.temp_dir).resolve()))

    def test_output_dir_management(self):
        out_sub = Path(self.temp_dir) / "MY_EXPORTS"
        set_output_dir(out_sub)
        self.assertEqual(get_output_dir(), str(out_sub.resolve()))

if __name__ == "__main__":
    unittest.main()

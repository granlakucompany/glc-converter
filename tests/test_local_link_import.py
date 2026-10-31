"""
Test unitaire et d'intégration : Ajout et ouverture de lien local (Étape 1)
"""
import sys
import unittest
from pathlib import Path
from PySide6.QtCore import Qt, QUrl
from PySide6.QtWidgets import QApplication

from src.core.mime_detector import MimeDetector
from src.core.converter_engine import ConversionTask, clean_base_stem
from src.ui.drop_zone import DropZoneWidget
from src.ui.link_input_dialog import LocalLinkDialog
from src.ui.main_window import MainWindow

app = QApplication.instance() or QApplication(sys.argv)

class TestLocalLinkImport(unittest.TestCase):
    def test_mime_detector_url(self):
        url = "http://localhost:3000/anim"
        info = MimeDetector.identify_file(url)
        self.assertTrue(info.get("valid"))
        self.assertTrue(info.get("is_url"))
        self.assertEqual(info.get("category"), "web")
        self.assertEqual(info.get("extension"), "html")
        self.assertEqual(info.get("size_formatted"), "URL Web")
        self.assertIn("localhost:3000", info.get("name"))

    def test_clean_base_stem_url(self):
        stem1 = clean_base_stem("http://localhost:3000/my-animation")
        self.assertIn("my-animation", stem1)

        stem2 = clean_base_stem("http://localhost:8800/")
        self.assertTrue(len(stem2) > 0)
        self.assertNotIn(":", stem2)

    def test_link_dialog_normalization(self):
        dlg = LocalLinkDialog()
        # Test 1: localhost sans http://
        dlg.txt_url.setText("localhost:5173/stage")
        dlg._on_validate()
        self.assertEqual(dlg.get_link(), "http://localhost:5173/stage")

        # Test 2: 127.0.0.1 sans http://
        dlg.txt_url.setText("127.0.0.1:8000")
        dlg._on_validate()
        self.assertEqual(dlg.get_link(), "http://127.0.0.1:8000")

        # Test 3: URL complète
        dlg.txt_url.setText("http://localhost:3000")
        dlg._on_validate()
        self.assertEqual(dlg.get_link(), "http://localhost:3000")

    def test_drop_zone_has_link_button(self):
        dz = DropZoneWidget()
        self.assertTrue(hasattr(dz, "btn_link"))
        self.assertIsNotNone(dz.btn_link)

        # Vérification du libellé Kadans / HTML
        dz.retranslate_ui("fr")
        self.assertIn("Kadans", dz.btn_link.text())

        dz.retranslate_ui("ht")
        self.assertIn("Kadans", dz.btn_link.text())

    def test_link_dialog_has_composition_browse(self):
        dlg = LocalLinkDialog()
        self.assertTrue(hasattr(dlg, "btn_browse_comp"))
        self.assertIn("composition.html", dlg.btn_browse_comp.text())

    def test_main_window_add_local_link(self):
        window = MainWindow(is_light_mode=True)
        test_url = "http://localhost:3000/intro"
        window._on_files_added([test_url])

        # Vérification dans la liste des tâches
        self.assertEqual(len(window.tasks), 1)
        task = window.tasks[0]
        self.assertEqual(task.input_path, test_url)
        self.assertEqual(task.output_format, "mp4")
        self.assertEqual(task.file_info.get("category"), "web")

        # Vérification de l'affichage dans la table
        self.assertEqual(window.task_table.rowCount(), 1)
        item = window.task_table.item(0, 1)
        self.assertIsNotNone(item)
        self.assertIn("localhost:3000", item.text())

        # Vérification dans l'inspecteur média
        self.assertEqual(window.preview_card.current_filepath, test_url)
        self.assertTrue(window.preview_card.is_html_mode)
        self.assertEqual(window.preview_card.lbl_badge_category.text(), "WEB")

        window.close()

    def test_convert_local_composition_to_video(self):
        import tempfile
        from src.core.converter_engine import ConverterEngine

        tmp_dir = Path(tempfile.gettempdir()) / "glc_kadans_test"
        tmp_dir.mkdir(parents=True, exist_ok=True)
        comp_file = tmp_dir / "composition.html"
        comp_file.write_text("""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Kadans WASDEV Animation</title>
</head>
<body style="margin:0; background:#0f172a; display:flex; justify-content:center; align-items:center; height:100vh;">
  <div id="stage" data-width="640" data-height="360" data-duration="1.0" data-fps="24" style="width:640px; height:360px; background:#7c3aed; display:flex; align-items:center; justify-content:center;">
    <h1 style="color:#ffffff; font-family:sans-serif; font-size:24px;">KADANS WASDEV LIVE</h1>
  </div>
</body>
</html>""", encoding="utf-8")

        task = ConversionTask(
            task_id="t_kadans",
            input_path=str(comp_file),
            output_format="mp4",
            output_dir=str(tmp_dir),
            options={"duration": 1.0, "fps": 24, "width": 640, "height": 360}
        )

        engine = ConverterEngine()
        engine.process_task(task)
        self.assertEqual(task.status, "Terminé")
        self.assertEqual(task.progress, 100.0)
        self.assertTrue(Path(task.output_path).exists())
        self.assertTrue(Path(task.output_path).stat().st_size > 500)

        # Nettoyage
        try:
            Path(task.output_path).unlink(missing_ok=True)
            comp_file.unlink(missing_ok=True)
        except Exception:
            pass

if __name__ == "__main__":
    unittest.main()

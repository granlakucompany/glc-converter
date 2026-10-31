"""
GLC CONVERTER — Suite de Tests Automatisés Complète
Éditeur: GRAN LAKU COMPANY | https://granlaku.com/glcconverter
"""
import unittest
import os
import tempfile
from pathlib import Path
from PIL import Image

from src.core.mime_detector import MimeDetector
from src.core.graph_router import GraphRouter
from src.core.hw_accel import HardwareDetector
from src.core.image_engine import ImageEngine
from src.core.html_video_engine import HtmlVideoEngine

class TestGlcConverter(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def test_01_hardware_detector(self):
        hw = HardwareDetector.get_instance()
        self.assertGreater(hw.cpu_cores, 0)
        summary = hw.get_summary_text()
        self.assertIn("Processeur", summary)

    def test_02_graph_router(self):
        router = GraphRouter()
        path = router.find_shortest_path("mp4", "mkv")
        self.assertIsNotNone(path)
        self.assertEqual(len(path), 1)

        path_audio = router.find_shortest_path("mp4", "mp3")
        self.assertIsNotNone(path_audio)

    def test_03_image_conversion(self):
        src_png = os.path.join(self.temp_dir, "test_input.png")
        dst_webp = os.path.join(self.temp_dir, "test_output.webp")
        dst_jpg = os.path.join(self.temp_dir, "test_output.jpg")
        dst_12k = os.path.join(self.temp_dir, "test_12k.webp")

        img = Image.new("RGBA", (100, 100), color=(139, 92, 246, 255))
        img.save(src_png)

        info = MimeDetector.identify_file(src_png)
        self.assertEqual(info["category"], "image")

        ok_webp = ImageEngine.convert_image(src_png, dst_webp, quality=85)
        self.assertTrue(ok_webp)
        self.assertTrue(os.path.exists(dst_webp))

        ok_jpg = ImageEngine.convert_image(src_png, dst_jpg, quality=90)
        self.assertTrue(ok_jpg)
        self.assertTrue(os.path.exists(dst_jpg))

        # Test conversion résolution 12K DCI (12288x6480)
        ok_12k = ImageEngine.convert_image(src_png, dst_12k, quality=75, resolution="12288x6480")
        self.assertTrue(ok_12k)
        self.assertTrue(os.path.exists(dst_12k))
        with Image.open(dst_12k) as im12:
            self.assertEqual(im12.size, (12288, 6480))

    def test_04_html_to_video(self):
        src_html = os.path.join(self.temp_dir, "anim.html")
        dst_mp4 = os.path.join(self.temp_dir, "anim.mp4")

        with open(src_html, "w", encoding="utf-8") as f:
            f.write("<body style='background:#0f0b1a;'><h1 style='color:#fbbf24;'>GLC</h1></body>")

        ok = HtmlVideoEngine.convert_html_to_video(
            src_html,
            dst_mp4,
            duration_sec=0.5,
            fps=30,
            width=320,
            height=240
        )
        self.assertTrue(ok)
        self.assertTrue(os.path.exists(dst_mp4))
        self.assertGreater(os.path.getsize(dst_mp4), 1000)

if __name__ == "__main__":
    unittest.main()

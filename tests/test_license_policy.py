"""
Non-régression licences : GLC CONVERTER est vendu en logiciel fermé.
Aucun encodeur GPL (libx264, libx265…) ne doit être choisi ni livré.
"""
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import av
from PIL import Image

from src.core import codec_policy
from src.core.video_engine import VideoEngine
from tools import check_licenses

CONTAINERS = ["mp4", "mov", "mkv", "webm", "avi", "ts", "m2ts", "mxf", "flv", "wmv"]
CODECS = ["h264", "avc", "hevc", "h265", "av1", "vp9", "prores", "mpeg4"]


class TestLicensePolicy(unittest.TestCase):
    def test_source_never_names_a_gpl_encoder(self):
        """Seul codec_policy.py (la liste d'interdiction) peut citer un encodeur GPL entre guillemets."""
        names = "|".join(re.escape(n) for n in codec_policy.FORBIDDEN_ENCODERS)
        pattern = re.compile(r"[\"'](" + names + r")[\"']")
        offenders = []
        for path in (PROJECT_ROOT / "src").rglob("*.py"):
            if path.name == "codec_policy.py":
                continue
            for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if pattern.search(line):
                    offenders.append(f"{path.relative_to(PROJECT_ROOT)}:{line_no}")
        self.assertEqual(offenders, [])

    def test_chain_never_contains_a_forbidden_encoder(self):
        for codec in CODECS:
            for container in CONTAINERS:
                for allow_hw in (True, False):
                    chain = codec_policy.video_encoder_chain(codec, container, allow_hw)
                    with self.subTest(codec=codec, container=container, hw=allow_hw):
                        self.assertTrue(chain, "aucun encodeur proposé")
                        self.assertFalse(set(chain) & codec_policy.FORBIDDEN_ENCODERS)

    def test_every_container_has_a_usable_encoder(self):
        """Chaque conteneur proposé produit une vidéo, même sans carte graphique."""
        for container in CONTAINERS:
            with self.subTest(container=container):
                encoder, pix_fmt = codec_policy.pick_video_encoder("h264", container, 640, 360, allow_hw=False)
                self.assertTrue(codec_policy.is_allowed(encoder))

    def test_12k_still_has_an_encoder(self):
        for container in ("mp4", "mov", "mkv"):
            with self.subTest(container=container):
                encoder, _ = codec_policy.pick_video_encoder("h264", container, 12288, 6480)
                self.assertTrue(codec_policy.is_allowed(encoder))

    def test_real_encodes_use_only_allowed_encoders(self):
        used = []
        original = codec_policy.pick_video_encoder

        def spy(*args, **kwargs):
            result = original(*args, **kwargs)
            used.append(result[0])
            return result

        codec_policy.pick_video_encoder = spy
        try:
            with tempfile.TemporaryDirectory() as tmp:
                img = os.path.join(tmp, "src.png")
                Image.new("RGB", (640, 360), (60, 20, 90)).save(img)
                for ext in ("mp4", "mov", "webm", "avi"):
                    out = os.path.join(tmp, f"out.{ext}")
                    self.assertTrue(VideoEngine.image_to_video(img, out, duration_sec=0.5, fps=10))
                    with av.open(out) as container:
                        self.assertGreater(sum(1 for _ in container.decode(video=0)), 0)

                converted = os.path.join(tmp, "converted.mkv")
                self.assertTrue(VideoEngine.convert_video(os.path.join(tmp, "out.mp4"), converted))
                with av.open(converted) as container:
                    self.assertGreater(sum(1 for _ in container.decode(video=0)), 0)
        finally:
            codec_policy.pick_video_encoder = original
        self.assertTrue(used)
        self.assertFalse(set(used) & codec_policy.FORBIDDEN_ENCODERS)

    def test_source_does_not_import_gpl_packages(self):
        self.assertEqual(check_licenses.check_source_imports(), [])

    def test_shipped_dependencies_contain_no_gpl(self):
        """Échoue tant que PyAV embarque x264/x265 : à corriger avant tout empaquetage."""
        self.assertEqual(check_licenses.run_checks(), [])


if __name__ == "__main__":
    unittest.main()

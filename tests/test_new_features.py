"""
Test des nouvelles fonctionnalités GLC CONVERTER :
- Formats du Plan (Vidéos, Images, Audio, Documents, Web/Lottie, 3D)
- Conversion Image -> Vidéo (MP4)
- Rendu 3D 360°
- Options intelligentes par catégorie
"""
import sys
import os
import tempfile
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image

from PySide6.QtWidgets import QApplication

from src.core.converter_engine import ConverterEngine, ConversionTask
from src.core.model3d_engine import Model3DEngine
from src.ui.preset_panel import PresetPanel

def run_tests():
    app = QApplication.instance() or QApplication(sys.argv)
    panel = PresetPanel()

    print("1. Vérification des catégories de formats du Plan :")
    categories = ['video', 'image', 'audio', 'document', 'web', '3d']
    for cat in categories:
        opts = panel.get_options_for_category(cat)
        fmt = opts.get("output_format")
        print(f"   [OK] Catégorie '{cat}' -> format cible: '{fmt}'")
        assert fmt is not None

    print("\n2. Test de rendu 3D 360° :")
    tmp_dir = tempfile.gettempdir()
    obj_file = os.path.join(tmp_dir, "test_cube.obj")
    with open(obj_file, "w") as f:
        f.write("v -1 -1 -1\nv 1 -1 -1\nv 1 1 -1\nv -1 1 -1\nv -1 -1 1\nv 1 -1 1\nv 1 1 1\nv -1 1 1\n")

    out_3d_mp4 = os.path.join(tmp_dir, "test_cube_360.mp4")
    success_3d = Model3DEngine.convert_3d(obj_file, out_3d_mp4, duration_sec=1.0, fps=15)
    print(f"   [OK] Rendu 3D vers MP4: {success_3d}, Taille: {os.path.getsize(out_3d_mp4)} octets")
    assert success_3d and os.path.exists(out_3d_mp4)

    print("\n3. Test Image PNG -> Vidéo MP4 (résolution 1080p) :")
    img = Image.new("RGB", (1280, 720), color=(88, 28, 135))
    img_in = os.path.join(tmp_dir, "test_slide.png")
    img.save(img_in)

    engine = ConverterEngine()
    task = ConversionTask("t_img_mp4", img_in, "mp4", tmp_dir, options={"output_format": "mp4", "duration": 1.0, "fps": 15})
    engine.process_task(task)
    print(f"   [OK] Conversion Image -> MP4: Statut = {task.status}, Taille: {os.path.getsize(task.output_path)} octets")
    assert task.status == "Terminé" and os.path.exists(task.output_path)

    print("\n TOUS LES TESTS SONT AU VERT !")

if __name__ == "__main__":
    run_tests()

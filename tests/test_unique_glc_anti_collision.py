"""
GLC CONVERTER — Tests Unitaires du Système Anti-Collision et Codes Uniques GLC
Éditeur: GRAN LAKU COMPANY | https://granlaku.com/glcconverter
"""
import unittest
import os
import tempfile
import re
from pathlib import Path
from PIL import Image

from src.core.converter_engine import (
    ConversionTask, ConverterEngine,
    clean_base_stem, generate_unique_glc_output_path,
    clear_allocated_output_paths
)
from src.core.image_engine import ImageEngine

class TestUniqueGlcAntiCollision(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        clear_allocated_output_paths()

    def tearDown(self):
        clear_allocated_output_paths()

    def test_01_clean_base_stem(self):
        """Vérifie que les suffixes répétitifs _glc, _GLC, et anciens codes sont nettoyés."""
        self.assertEqual(clean_base_stem("video.mp4"), "video")
        self.assertEqual(clean_base_stem("video_glc.mp4"), "video")
        self.assertEqual(clean_base_stem("composition_glc_glc.mp4"), "composition")
        self.assertEqual(clean_base_stem("01_glc.webp"), "01")
        self.assertEqual(clean_base_stem("cinema_GLC_A7F9B2C4.mp4"), "cinema")
        self.assertEqual(clean_base_stem("test_GLC_12345678_glc.mp4"), "test")
        # Cas limite vide
        self.assertEqual(clean_base_stem(".mp4"), "media")

    def test_02_default_glc_naming_and_unique_code(self):
        """Vérifie la génération par défaut contenant 'GLC' et un code unique de 8 caractères."""
        input_file = os.path.join(self.temp_dir, "mon_animation.html")
        task = ConversionTask(
            task_id="TASK0001",
            input_path=input_file,
            output_format="mp4",
            output_dir=self.temp_dir
        )
        self.assertTrue(hasattr(task, "unique_code"))
        self.assertEqual(len(task.unique_code), 8)
        self.assertTrue(task.unique_code.isalnum())
        self.assertTrue(task.unique_code.isupper())

        # Le nom de sortie doit respecter le pattern: {stem}_GLC_{code}.{format}
        expected_pattern = rf"mon_animation_GLC_[0-9A-Z]{{8}}\.mp4$"
        self.assertRegex(Path(task.output_path).name, expected_pattern)
        self.assertIn("GLC", Path(task.output_path).name)

    def test_03_anti_collision_same_file_same_folder(self):
        """Vérifie que 2 conversions du même fichier dans le même dossier ont des codes différents."""
        input_file = os.path.join(self.temp_dir, "clip.mp4")
        task1 = ConversionTask(
            task_id="ID_0001",
            input_path=input_file,
            output_format="mp4",
            output_dir=self.temp_dir
        )
        task2 = ConversionTask(
            task_id="ID_0002",
            input_path=input_file,
            output_format="mp4",
            output_dir=self.temp_dir
        )

        # Les codes uniques et les chemins de sortie doivent être strictement différents
        self.assertNotEqual(task1.unique_code, task2.unique_code)
        self.assertNotEqual(task1.output_path, task2.output_path)
        self.assertNotEqual(Path(task1.output_path).name, Path(task2.output_path).name)

    def test_04_no_overwrite_when_file_already_exists_on_disk(self):
        """Vérifie qu'un fichier existant sur le disque n'est JAMAIS écrasé."""
        # Créer manuellement un fichier cible avec un code précis sur le disque
        fixed_code = "A1B2C3D4"
        existing_filename = f"document_GLC_{fixed_code}.pdf"
        existing_filepath = os.path.join(self.temp_dir, existing_filename)
        with open(existing_filepath, "w", encoding="utf-8") as f:
            f.write("CONTENU_ORIGINAL_A_NE_JAMAIS_ECRASER")

        self.assertTrue(os.path.exists(existing_filepath))

        # Créer une tâche demandant le même code que le fichier existant
        task = ConversionTask(
            task_id=fixed_code.lower(),
            input_path=os.path.join(self.temp_dir, "document.docx"),
            output_format="pdf",
            output_dir=self.temp_dir
        )

        # La tâche doit avoir détecté la collision sur le disque et généré un nouveau code !
        self.assertNotEqual(task.output_path, existing_filepath)
        self.assertNotEqual(task.unique_code, fixed_code)
        self.assertTrue(os.path.exists(existing_filepath))

        # Le contenu du fichier original n'a pas été altéré
        with open(existing_filepath, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), "CONTENU_ORIGINAL_A_NE_JAMAIS_ECRASER")

    def test_05_real_conversion_anti_collision(self):
        """Exécute 2 conversions d'image réelles et vérifie que 2 fichiers distincts sont créés."""
        src_png = os.path.join(self.temp_dir, "photo.png")
        img = Image.new("RGB", (64, 64), color=(255, 0, 128))
        img.save(src_png)

        engine = ConverterEngine()

        # Première conversion
        task1 = ConversionTask(
            task_id="T1",
            input_path=src_png,
            output_format="webp",
            output_dir=self.temp_dir
        )
        engine.process_task(task1)
        self.assertEqual(task1.status, "Terminé")
        self.assertTrue(os.path.exists(task1.output_path))

        # Deuxième conversion du même fichier vers le même format dans le même dossier
        task2 = ConversionTask(
            task_id="T2",
            input_path=src_png,
            output_format="webp",
            output_dir=self.temp_dir
        )
        engine.process_task(task2)
        self.assertEqual(task2.status, "Terminé")
        self.assertTrue(os.path.exists(task2.output_path))

        # Vérification formelle : Les deux fichiers existent côte à côte sans écrasement
        self.assertNotEqual(task1.output_path, task2.output_path)
        self.assertNotEqual(task1.unique_code, task2.unique_code)
        self.assertTrue(os.path.exists(task1.output_path))
        self.assertTrue(os.path.exists(task2.output_path))

if __name__ == "__main__":
    unittest.main()

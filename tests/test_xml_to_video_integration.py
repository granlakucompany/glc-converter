"""
GLC CONVERTER — Test d'Intégration Complète XML vers Vidéo Ultra-HD
Vérifie la détection MIME, la lecture des métadonnées XML/SVG, le rendu vidéo et l'interface utilisateur.
"""
import sys
import os
from pathlib import Path

# Fix Windows console UTF-8 output
sys.stdout.reconfigure(encoding="utf-8")

# Définir le chemin racine
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from src.core.mime_detector import MimeDetector
from src.core.html_detector import HtmlDetector
from src.core.converter_engine import ConverterEngine, ConversionTask
from src.ui.process_bar import ProcessProgressBar

def run_all_tests():
    app = QApplication.instance() or QApplication(sys.argv)
    print("==================================================")
    print("▶ TEST 1: Détection MIME pour les fichiers .xml / .xhtml")
    print("==================================================")
    
    test_xml_path = project_root / "tests" / "test_animation.xml"
    test_xml_path.write_text("""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080" width="1920" height="1080">
    <rect width="1920" height="1080" fill="#0b0f19"/>
    <circle cx="960" cy="540" r="180" fill="#7c3aed">
        <animate attributeName="r" values="100;220;100" dur="3s" repeatCount="indefinite"/>
        <animate attributeName="fill" values="#7c3aed;#ec4899;#7c3aed" dur="3s" repeatCount="indefinite"/>
    </circle>
    <text x="960" y="555" font-family="Arial" font-size="44" font-weight="bold" fill="#ffffff" text-anchor="middle">
        GLC XML CONVERTER 4K
    </text>
</svg>
""", encoding="utf-8")

    info = MimeDetector.identify_file(str(test_xml_path))
    print(f"Catégorie détectée: {info.get('category')} (Attendu: web)")
    print(f"Type MIME détecté: {info.get('mime_type')} (Attendu: text/xml)")
    assert info.get("category") == "web", f"Échec: catégorie {info.get('category')}"
    assert info.get("mime_type") == "text/xml", f"Échec: mime_type {info.get('mime_type')}"
    print("✅ TEST 1 RÉUSSI : Identification MIME XML validée.")

    print("\n==================================================")
    print("▶ TEST 2: Détection Métadonnées XML / SVG via HtmlDetector")
    print("==================================================")
    meta = HtmlDetector.detect_html_metadata(str(test_xml_path))
    print(f"Largeur: {meta.get('width')} px (Attendu: 1920)")
    print(f"Hauteur: {meta.get('height')} px (Attendu: 1080)")
    print(f"Durée: {meta.get('duration')} s (Attendu: >= 3.0s)")
    assert meta.get("width") == 1920, f"Erreur largeur: {meta.get('width')}"
    assert meta.get("height") == 1080, f"Erreur hauteur: {meta.get('height')}"
    assert meta.get("duration") >= 3.0, f"Erreur durée: {meta.get('duration')}"
    print("✅ TEST 2 RÉUSSI : Métadonnées XML / SVG correctement extraites.")

    print("\n==================================================")
    print("▶ TEST 3: Libellé Explicite dans la Barre de Progression")
    print("==================================================")
    task = ConversionTask(
        task_id="test_xml_01",
        input_path=str(test_xml_path),
        output_format="mp4",
        output_dir=str(project_root / "tests"),
        options={"resolution": "3840x2160", "crf": 16},
        file_info=info
    )
    pb = ProcessProgressBar()
    label = pb._get_target_conversion_label(task)
    print(f"Libellé cible généré: '{label}'")
    assert "4K UHD" in label and "MP4" in label, f"Libellé incorrect: {label}"
    print("✅ TEST 3 RÉUSSI : Libellé 4K UHD (MP4) généré avec succès pour XML.")

    print("\n==================================================")
    print("▶ TEST 4: Conversion Déterministe XML vers MP4")
    print("==================================================")
    out_mp4 = project_root / "tests" / "test_xml_output.mp4"
    if out_mp4.exists():
        out_mp4.unlink()

    engine = ConverterEngine()
    progress_updates = []
    
    def on_prog(t):
        progress_updates.append(t.progress)

    # Lancer la conversion (durée 1 seconde à 30 fps pour un test unitaire ultra-rapide)
    task.options["duration"] = 1.0
    task.options["fps"] = 30
    task.options["resolution"] = "1920x1080"
    task.output_path = str(out_mp4)

    engine.process_task(task, on_progress=on_prog)
    print(f"Statut tâche: {task.status}")
    print(f"Fichier de sortie existe: {out_mp4.exists()}")
    if out_mp4.exists():
        size_kb = out_mp4.stat().st_size / 1024
        print(f"Taille de la vidéo produite: {size_kb:.2f} Ko")
        assert size_kb > 10, "La vidéo produite est anormalement petite !"
    assert task.status == "Terminé", f"Échec de la tâche: {task.error_message}"
    print("✅ TEST 4 RÉUSSI : Rendu vidéo XML vers MP4 réussi avec succès.")

    # Nettoyage
    try:
        if out_mp4.exists(): out_mp4.unlink()
        if test_xml_path.exists(): test_xml_path.unlink()
    except Exception:
        pass

    print("\n==================================================")
    print("TOUS LES TESTS D'INTÉGRATION XML VERS VIDÉO SONT VALIDÉS (100% OK)")
    print("==================================================")

if __name__ == "__main__":
    run_all_tests()

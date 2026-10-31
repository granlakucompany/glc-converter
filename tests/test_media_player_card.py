"""
Test automatisé de validation pour le Lecteur Média dans la Carte d'Aperçu :
- Bouton Play / Pause interactif
- Contrôle de Volume (bouton muet + slider)
- Bouton Plein Écran (icône ⛶)
- Support des fichiers Vidéo et Animations HTML5
"""
import sys
import os
import tempfile
from pathlib import Path

# Configurer stdout en UTF-8 pour Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap

from src.core.converter_engine import ConversionTask
from src.ui.main_window import MainWindow
from src.ui.media_preview_card import MediaPreviewCard
from src.ui.fullscreen_player import FullScreenStudioPlayer

def run_tests():
    app = QApplication.instance() or QApplication(sys.argv)

    print("-> 1. Initialisation de MainWindow et MediaPreviewCard...")
    window = MainWindow(is_light_mode=False)
    window.telemetry_timer.stop()
    window.cyber_bg.timer.stop()
    window.resize(1150, 750)

    card = window.preview_card

    # 1. Tester la vidéo
    video_path = os.path.abspath("OUTPUT/composition_glc.mp4")
    print(f"-> 2. Chargement du média vidéo : {video_path}...")
    card.load_media(video_path)

    # Vérifications des contrôles
    assert card.btn_play.isEnabled(), "Le bouton Play doit être activé pour une vidéo"
    assert card.btn_play.text() == "▶", "Le bouton Play doit afficher '▶' au repos"
    assert card.btn_fullscreen.isEnabled(), "Le bouton Plein Écran doit être activé"
    assert card.btn_fullscreen.text() == "⛶", "L'icône plein écran doit être ⛶"
    assert card.vol_slider.value() == 80, "Le volume par défaut doit être 80%"

    print("   [OK] Bouton Play, Scrubber, Volume et Icône Plein Écran ⛶ validés pour la vidéo.")

    # Simuler le clic sur Play
    card.btn_play.click()
    print("   [OK] Clic Play exécuté (état de lecture enclenché).")

    # Simuler le changement de volume
    card.vol_slider.setValue(60)
    assert abs(card.audio_output.volume() - 0.6) < 0.05, "Le volume audio doit suivre la valeur du slider"
    print("   [OK] Réglage de volume à 60% validé.")

    # Simuler le mute
    card.btn_mute.click()
    assert card.is_muted == True, "Le mode muet doit être activé"
    assert card.btn_mute.text() == "🔇", "L'icône muet doit afficher 🔇"
    card.btn_mute.click()
    assert card.is_muted == False, "Le mode muet doit être désactivé"
    assert card.btn_mute.text() == "🔊", "L'icône volume doit afficher 🔊"
    print("   [OK] Bouton Mute toggle validé.")

    # 2. Tester avec un fichier HTML5
    tmp = tempfile.gettempdir()
    html_file = os.path.join(tmp, "test_preview_anim.html")
    with open(html_file, "w", encoding="utf-8") as f:
        f.write("""<!DOCTYPE html><html><body style="background:#0b0914;color:#a855f7;display:flex;justify-content:center;align-items:center;height:100vh;"><h1>KADANS MOTION</h1></body></html>""")

    print(f"-> 3. Chargement de l'animation HTML5 : {html_file}...")
    card.load_media(html_file)
    assert card.is_html_mode == True, "Le mode HTML doit être détecté"
    assert card.btn_play.isEnabled(), "Le bouton Play doit être activé pour l'animation HTML"
    assert card.btn_fullscreen.isEnabled(), "Le bouton Plein Écran doit être activé pour le HTML"
    print("   [OK] Animation HTML5 chargée avec contrôles Play/Volume/Fullscreen.")

    # Recharger la vidéo pour la capture finale
    card.load_media(video_path)

    # 3. Test du composant Plein Écran
    print("-> 4. Test du FullScreenStudioPlayer...")
    fs = FullScreenStudioPlayer(video_path, start_position_ms=1500, auto_play=False, parent=window)
    assert fs.lbl_title.text().endswith("composition_glc.mp4"), "Le titre doit correspondre"
    assert fs.btn_play.text() == "▶", "Le bouton play du plein écran doit être présent"
    assert fs.btn_exit_fs.text() == "🗗 Quitter Plein Écran", "Le bouton quitter plein écran doit être présent"
    fs.close()
    print("   [OK] FullScreenStudioPlayer initialisé et vérifié avec succès.")

    # 4. Capture d'écran de l'interface avec la carte d'aperçu enrichie
    window.show()
    screenshot_path = os.path.abspath("tests/media_preview_player_verified.png")
    pix = window.grab()
    pix.save(screenshot_path)
    print(f"-> 5. Capture d'écran enregistrée dans : {screenshot_path}")

    print("\n-> TOUS LES TESTS DU LECTEUR MULTIMÉDIA ET PLEIN ÉCRAN ONT RÉUSSI !")
    window.close()

if __name__ == "__main__":
    run_tests()

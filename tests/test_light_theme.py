"""
Test et capture visuelle du THÈME CLAIR (Light Studio Theme) :
1. Splash Screen Futuriste en Thème Clair
2. Fenêtre Principale en Thème Clair avec Cartes Didactiques 1-2-3, Tableau Centré et Inspecteur
3. Bascule dynamique vers Thème Sombre et retour vers Thème Clair
"""
import sys
import os
import tempfile
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from src.core.converter_engine import ConversionTask
from src.ui.theme import get_theme_stylesheet, LIGHT_THEME_STYLE, DARK_THEME_STYLE
from src.ui.splash_screen import FuturisticSplashScreen
from src.ui.main_window import MainWindow

def test_light_theme_and_capture():
    app = QApplication.instance() or QApplication(sys.argv)
    app.setStyleSheet(get_theme_stylesheet(True))

    print("1. Vérification des styles de Thème Clair & Sombre :")
    assert "background-color: #f8fafc;" in LIGHT_THEME_STYLE
    assert "background-color: #050507;" in DARK_THEME_STYLE
    print("   [OK] Styles QSS valides")

    # 2. Test et capture du Splash Screen en Thème Clair
    print("\n2. Test du Splash Screen Futuriste (Thème Clair) :")
    splash = FuturisticSplashScreen(is_light_mode=True)
    splash.timer.stop()
    splash.current_progress = 75.0
    splash.status_text = "◈ [04/05] CHARGEMENT DE LA MATRICE UNIVERSELLE DES FORMATS..."
    splash.show()
    app.processEvents()

    splash_pix = splash.grab()
    splash_out = os.path.abspath("tests/splash_screen_light_preview.png")
    os.makedirs(os.path.dirname(splash_out), exist_ok=True)
    splash_pix.save(splash_out)
    print(f"   [OK] Capture Splash Screen Clair sauvegardée dans : {splash_out}")
    splash.close()

    # 3. Test de la Fenêtre Principale en Thème Clair
    print("\n3. Test de la Fenêtre Principale (Thème Clair) :")
    window = MainWindow(is_light_mode=True)
    window.telemetry_timer.stop()
    window.cyber_bg.timer.stop()
    window.resize(1300, 860)

    # Peupler la file d'attente avec des formats variés
    tmp = tempfile.gettempdir()
    mock_tasks = [
        ("bande_annonce_cinema_12k.mp4", "mp4", "webm", "182.4 Mo"),
        ("affiche_officielle_glc.png", "png", "webp", "14.2 Mo"),
        ("bande_son_orchestre.wav", "wav", "flac", "64.8 Mo"),
        ("contrat_distribution_studio.pdf", "pdf", "docx", "2.1 Mo"),
        ("logo_3d_rotatif.obj", "obj", "mp4", "5.8 Mo")
    ]

    for fname, ext, out_fmt, size_str in mock_tasks:
        fpath = os.path.join(tmp, fname)
        if not os.path.exists(fpath):
            with open(fpath, "w") as f:
                f.write("mock media")

        t = ConversionTask(
            task_id=f"id_{ext}",
            input_path=fpath,
            output_format=out_fmt,
            output_dir=tmp,
            options={"output_format": out_fmt}
        )
        t.file_info = {"extension": ext, "size_formatted": size_str}
        window.tasks.append(t)
        window.task_table.add_task(t)

    # Simuler des états réalistes
    window.tasks[0].status = "Terminé"
    window.tasks[0].progress = 100.0
    window.tasks[0].speed = 186.4
    window.task_table.update_task_progress(window.tasks[0])

    window.tasks[1].status = "En cours"
    window.tasks[1].progress = 62.0
    window.tasks[1].speed = 94.1
    window.tasks[1].eta = "00:02"
    window.task_table.update_task_progress(window.tasks[1])

    window.preview_card.inspect_task(window.tasks[0])

    window.show()
    app.processEvents()

    # Capture en Thème Clair
    main_pix = window.grab()
    main_out = os.path.abspath("tests/main_window_light_preview.png")
    main_pix.save(main_out)
    print(f"   [OK] Capture Fenêtre Principale Clair sauvegardée dans : {main_out}")

    # 4. Test du bouton de bascule Thème (Toggle Clair <-> Sombre)
    print("\n4. Test de la Bascule Dynamique Clair <-> Sombre :")
    window._toggle_theme()
    assert window.is_light_mode is False
    assert window.cyber_bg.is_light_mode is False
    assert "☀️" in window.btn_theme_toggle.text()
    print("   [OK] Bascule vers Thème Sombre réussie")

    window._toggle_theme()
    assert window.is_light_mode is True
    assert window.cyber_bg.is_light_mode is True
    assert "🌙" in window.btn_theme_toggle.text()
    print("   [OK] Retour vers Thème Clair réussi")

    print("\n TOUS LES TESTS DU THÈME CLAIR SONT AU VERT ET VALIDÉS !")
    window.close()

if __name__ == "__main__":
    test_light_theme_and_capture()
    sys.exit(0)

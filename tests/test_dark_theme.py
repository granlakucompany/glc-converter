"""
Test et capture visuelle du THÈME SOMBRE STUDIO (Dark Theme) :
Vérification que le Thème Sombre est le thème par défaut pour le confort des yeux :
- Fond noir profond #050507 sans agressivité lumineuse
- Boutons et accents mauve studio élégants
- Tableau centré haute précision avec cases à cocher carrées [✓]
- Splash screen haute technologie néon violet
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
from src.ui.theme import get_theme_stylesheet, STUDIO_STYLE, DARK_THEME_STYLE, LIGHT_THEME_STYLE
from src.ui.splash_screen import FuturisticSplashScreen
from src.ui.main_window import MainWindow

def test_dark_theme_and_capture():
    app = QApplication.instance() or QApplication(sys.argv)
    
    print("1. Vérification du Thème Sombre par défaut :")
    assert STUDIO_STYLE == DARK_THEME_STYLE, "STUDIO_STYLE doit être DARK_THEME_STYLE"
    assert get_theme_stylesheet() == DARK_THEME_STYLE, "get_theme_stylesheet() sans argument doit retourner DARK_THEME_STYLE"
    assert get_theme_stylesheet(False) == DARK_THEME_STYLE, "get_theme_stylesheet(False) doit retourner DARK_THEME_STYLE"
    assert get_theme_stylesheet(True) == LIGHT_THEME_STYLE, "get_theme_stylesheet(True) doit retourner LIGHT_THEME_STYLE"
    print("   [OK] Le Thème Sombre Studio est bien défini comme thème par défaut.")

    # Appliquer le thème sombre par défaut à l'application
    app.setStyleSheet(get_theme_stylesheet(False))

    # 2. Test et capture du Splash Screen en Thème Sombre
    print("\n2. Test du Splash Screen Futuriste (Thème Sombre) :")
    splash = FuturisticSplashScreen()  # default is_light_mode=False
    assert not splash.is_light_mode, "Le splash screen doit démarrer en mode sombre par défaut"
    splash.timer.stop()
    splash.current_progress = 72.0
    splash.status_text = "◈ [03/05] DÉVERROUILLAGE PIPELINE 12K DCI CINEMA (12288×6480)..."
    splash.show()
    app.processEvents()

    splash_pix = splash.grab()
    splash_out = os.path.abspath("tests/splash_dark_preview.png")
    os.makedirs(os.path.dirname(splash_out), exist_ok=True)
    splash_pix.save(splash_out)
    print(f"   [OK] Capture Splash Screen Sombre sauvegardée dans : {splash_out}")
    splash.close()

    # 3. Test de la Fenêtre Principale en Thème Sombre
    print("\n3. Test de la Fenêtre Principale (Thème Sombre Studio) :")
    window = MainWindow()  # default is_light_mode=False
    assert not window.is_light_mode, "La fenêtre principale doit démarrer en mode sombre par défaut"
    assert window.btn_theme_toggle.text() == "☀️ Clair", "En mode sombre, le bouton doit proposer '☀️ Clair'"
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
        ("modele_3d_rotatif.obj", "obj", "mp4", "5.8 Mo")
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
    window._update_status_bar()

    # Vérification de l'affichage de la dernière version dans le bottom (Barre d'état)
    assert hasattr(window, "btn_version_badge"), "La barre d'état doit posséder le badge de version"
    assert "1.0.0 Pro Studio Edition" in window.btn_version_badge.text(), "Le badge de version doit contenir la dernière version"
    assert "1.0.0 Pro Studio Edition" in window.status_bar.currentMessage(), "Le message de status bar doit afficher la dernière version"
    safe_badge_text = window.btn_version_badge.text().encode('ascii', 'replace').decode('ascii')
    print(f"   [OK] Derniere version bien affichee dans le bottom : Badge '{safe_badge_text}'")

    window.show()
    app.processEvents()

    # Capture en Thème Sombre
    main_pix = window.grab()
    main_out = os.path.abspath("tests/main_window_dark_preview.png")
    main_pix.save(main_out)
    print(f"   [OK] Capture Fenêtre Principale Sombre sauvegardée dans : {main_out}")

    # 4. Test du bouton de bascule vers le thème clair puis retour vers le sombre
    print("\n4. Test de bascule dynamique :")
    window.btn_theme_toggle.click()
    app.processEvents()
    assert window.is_light_mode is True, "Après clic, doit être en Thème Clair"
    assert window.btn_theme_toggle.text() == "🌙 Sombre"
    print("   [OK] Bascule vers Thème Clair réussie")

    window.btn_theme_toggle.click()
    app.processEvents()
    assert window.is_light_mode is False, "Après second clic, doit revenir en Thème Sombre"
    assert window.btn_theme_toggle.text() == "☀️ Clair"
    print("   [OK] Retour au Thème Sombre réussi")

    window.close()
    print("\n=== TOUS LES TESTS DU THÈME SOMBRE ONT RÉUSSI AVEC SUCCÈS ===")

if __name__ == "__main__":
    test_dark_theme_and_capture()

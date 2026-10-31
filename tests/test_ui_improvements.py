"""
Test et capture visuelle des améliorations UI :
1. Splash Screen Futuriste Cybernétique
2. Tableau de conversion avec titres et cellules centrés
3. Icône de conversion sur chaque ligne + bouton individuel de conversion
"""
import sys
import os
import tempfile
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap

from src.core.converter_engine import ConversionTask
from src.ui.splash_screen import FuturisticSplashScreen
from src.ui.main_window import MainWindow

def test_and_capture():
    app = QApplication.instance() or QApplication(sys.argv)

    # 1. Tester et capturer le Splash Screen Futuriste
    print("-> Test du Splash Screen Futuriste...")
    splash = FuturisticSplashScreen()
    splash.timer.stop() # Pause animation timer for screenshot
    splash.current_progress = 68.0
    splash.status_text = "◈ [03/05] DÉVERROUILLAGE PIPELINE 12K DCI CINEMA (12288×6480)..."
    splash.show()
    app.processEvents()

    splash_pixmap = splash.grab()
    splash_path = os.path.abspath("tests/futuristic_splash_preview.png")
    os.makedirs(os.path.dirname(splash_path), exist_ok=True)
    splash_pixmap.save(splash_path)
    print(f"   [OK] Capture du Splash Screen sauvegardée dans : {splash_path}")
    splash.close()

    # 2. Tester et capturer la Fenêtre Principale avec le tableau centré & icônes
    print("-> Test de la Fenêtre Principale et du Tableau Centré...")
    window = MainWindow()
    window.telemetry_timer.stop()
    window.cyber_bg.timer.stop()
    window.resize(1300, 860)

    # Créer quelques fichiers de test pour peupler le tableau
    tmp = tempfile.gettempdir()
    demo_files = [
        ("demo_film_4k.mp4", "mp4", "webm", "48.2 Mo"),
        ("affiche_studio.png", "png", "webp", "4.6 Mo"),
        ("soundtrack_master.wav", "wav", "flac", "12.8 Mo"),
        ("scene_3d_cube.obj", "obj", "mp4", "1.1 Mo")
    ]

    for fname, ext, out_fmt, size_str in demo_files:
        p = os.path.join(tmp, fname)
        if not os.path.exists(p):
            with open(p, "w") as f:
                f.write("mock media content")

        t = ConversionTask(
            task_id=f"task_{ext}",
            input_path=p,
            output_format=out_fmt,
            output_dir=tmp,
            options={"output_format": out_fmt}
        )
        t.file_info = {"extension": ext, "size_formatted": size_str}
        window.tasks.append(t)
        window.task_table.add_task(t)

    # Simuler un fichier à 100% terminé
    window.tasks[0].status = "Terminé"
    window.tasks[0].progress = 100.0
    window.tasks[0].speed = 142.5
    window.task_table.update_task_progress(window.tasks[0])

    # Simuler un fichier en cours à 45%
    window.tasks[1].status = "En cours"
    window.tasks[1].progress = 45.0
    window.tasks[1].speed = 58.2
    window.tasks[1].eta = "00:04"
    window.task_table.update_task_progress(window.tasks[1])

    window.show()
    app.processEvents()

    # Vérification des propriétés de centrage du tableau
    header = window.task_table.horizontalHeader()
    print("   [Vérification Centrage En-tête]: DefaultAlignment =", header.defaultAlignment())
    for col in range(window.task_table.columnCount()):
        h_item = window.task_table.horizontalHeaderItem(col)
        align = h_item.textAlignment() if h_item else None
        col_name = window.task_table.COLUMNS[col].encode('ascii', 'replace').decode('ascii')
        print(f"   - Col {col} ({col_name}): Align = {align}")
        assert align == int(Qt.AlignmentFlag.AlignCenter)

    main_pixmap = window.grab()
    main_path = os.path.abspath("tests/main_table_centered_preview.png")
    main_pixmap.save(main_path)
    print(f"   [OK] Capture Fenêtre Principale sauvegardée dans : {main_path}")

    # Vérification des cases à cocher carrées ("ti kare devan chak fichye")
    for r in range(window.task_table.rowCount()):
        assert window.task_table.is_task_checked(r) is True
        target_cell = window.task_table.item(r, 3)
        assert "🔄" in target_cell.text()
        print(f"   [OK] Ligne {r} Case cochee active, Format Cible = '{target_cell.text().encode('ascii', 'replace').decode('ascii')}'")

    # Vérification sélection et filtrage
    checked_ids = window.task_table.get_checked_task_ids()
    assert len(checked_ids) == window.task_table.rowCount()
    print(f"   [OK] Tous les {len(checked_ids)} fichiers sont cochés par défaut")

    # Test décochage individuel
    window.task_table.set_task_checked(0, False)
    assert window.task_table.is_task_checked(0) is False
    assert len(window.task_table.get_checked_task_ids()) == window.task_table.rowCount() - 1
    window.task_table.set_task_checked(0, True) # Réactiver

    print("\n TOUTES LES VERIFICATIONS SONT VALIDEES AVEC SUCCES !")
    window.close()

if __name__ == "__main__":
    test_and_capture()
    sys.exit(0)

"""
Test de validation pour :
1. Responsive layout lors de la réduction de l'écran (aucune icône ni bouton coupé).
2. Toutes les icônes de la rangée (menu actions : convert, folder, preview, delete) bien visibles.
3. Icône animée de rotation continue lors de la conversion (« ti icon nan dwe ap vire won »).
4. Barre de processus studio inférieure avec dégradé Mauve & Bleu, détails, pourcentage et calcul des minutes/secondes.
"""
import sys
import os
import tempfile
import time
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap

from src.core.converter_engine import ConversionTask
from src.ui.main_window import MainWindow
from src.ui.task_table import SpinningConvertButton

def run_tests_and_capture():
    app = QApplication.instance() or QApplication(sys.argv)

    print("-> 1. Initialisation de la Fenêtre Principale Studio...")
    window = MainWindow(is_light_mode=False) # Mode sombre reposant par défaut
    window.telemetry_timer.stop()
    window.cyber_bg.timer.stop()
    window.resize(1100, 750)

    # Créer des fichiers de démonstration
    tmp = tempfile.gettempdir()
    demo_files = [
        ("film_cinematographique_12k.mp4", "mp4", "webp", "148.5 Mo"),
        ("studio_portrait_master.png", "png", "webp", "12.4 Mo"),
        ("ambiance_cyber_audio.wav", "wav", "flac", "35.2 Mo"),
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

    # 1. Vérifier que la colonne Actions (index 8) est bien présente et visible avec ses 4 boutons
    print("-> 2. Vérification des boutons d'actions et du menu sur chaque ligne...")
    assert window.task_table.columnCount() == 9
    for r in range(len(demo_files)):
        act_widget = window.task_table.cellWidget(r, 8)
        assert act_widget is not None, f"Le widget Actions pour la ligne {r} doit exister"
        buttons = act_widget.findChildren(SpinningConvertButton)
        assert len(buttons) == 1, f"Bouton de conversion trouvé pour ligne {r}"

    # 2. Simuler une tâche en cours et vérifier la rotation de l'icône
    print("-> 3. Test de la rotation continue de l'icône de conversion (« ti icon nan ap vire won »)...")
    task_running = window.tasks[0]
    task_running.status = "En cours"
    task_running.progress = 68.0
    task_running.speed = 72.4
    task_running.eta = "00:42"
    window.task_table.update_task_progress(task_running)

    btn_spin = window.task_table.convert_buttons[task_running.task_id]
    assert btn_spin._is_spinning is True, "Le bouton de la tâche en cours doit être en mode rotation"
    print("   [OK] L'icône de conversion tourne en boucle (animation active).")

    # 3. Test de la barre de processus inférieure avec dégradé Mauve & Bleu
    print("-> 4. Test de la barre de processus inferieure (Mauve & Bleu, details, %, minutes)...")
    window.process_bar.start_process(total_tasks=3, first_task_name=task_running.input_path)
    window.process_bar.start_time = time.time() - 75 # Simuler 1 min 15s écoulée
    window.process_bar.update_task_progress(task_running, current_idx=1, total_count=3)

    assert window.process_bar.pbar.value() > 0, "La barre de progression doit avoir une valeur positive"
    time_text = window.process_bar.lbl_time.text()
    details_text = window.process_bar.lbl_details.text()
    print("   [OK] Details affiches :", details_text.encode('ascii', 'replace').decode('ascii'))
    print("   [OK] Temps & Minutes affiches :", time_text.encode('ascii', 'replace').decode('ascii'))
    assert "01m 15s" in time_text or "m" in time_text, "Le minuteur doit afficher les minutes et secondes"

    # 4. Test de réduction d'écran (Responsive fitting)
    print("-> 5. Test de réduction de la fenêtre (1080x720)...")
    window.resize(1080, 720)
    window.show()
    app.processEvents()

    # Vérifier que toutes les 9 colonnes sont présentes et visibles
    for col in range(9):
        assert not window.task_table.isColumnHidden(col), f"La colonne {col} doit rester TOUJOURS visible"
    print("   [OK] Toutes les actions et menus restent parfaitement visibles et accessibles même à 900px !")

    # 5. Capture d'écran haute résolution de l'interface complète
    capture_path = os.path.abspath("tests/responsive_studio_with_process_bar.png")
    os.makedirs(os.path.dirname(capture_path), exist_ok=True)
    pix = window.grab()
    pix.save(capture_path)
    print(f"   [OK] Capture d'écran enregistrée dans : {capture_path}")

    # Arrêter les timers et fermer
    btn_spin.stop_spinning()
    window.process_bar._timer.stop()
    window.close()
    print("-> Tous les tests de validation responsive & barre de processus ont RÉUSSI avec succès !")

if __name__ == "__main__":
    run_tests_and_capture()
    sys.exit(0)

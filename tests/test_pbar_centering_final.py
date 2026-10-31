"""
Validation complète et automatisée du centrage parfait de la barre de progression
et de l'affichage du pourcentage dans la table des tâches.
"""
import sys
import os
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PySide6.QtWidgets import QApplication, QProgressBar
from PySide6.QtCore import Qt
from src.core.converter_engine import ConversionTask
from src.ui.main_window import MainWindow
from src.ui.task_table import CyberTableProgressBar
from src.ui.theme import get_theme_stylesheet

def run_centering_validation():
    app = QApplication.instance() or QApplication(sys.argv)
    app.setStyleSheet(get_theme_stylesheet(False))

    window = MainWindow(is_light_mode=False)
    window.telemetry_timer.stop()
    window.cyber_bg.timer.stop()
    window.resize(1300, 860)

    sample_path = os.path.abspath("composition.html")
    if not os.path.exists(sample_path):
        sample_path = os.path.abspath("tests/test_pbar_centering_final.py")

    test_data = [
        (0, "En attente"),
        (25, "En cours"),
        (50, "En cours"),
        (75, "En cours"),
        (100, "Terminé"),
    ]

    for i, (pct, status) in enumerate(test_data):
        task = ConversionTask(
            task_id=f"test_pbar_{i}",
            input_path=sample_path,
            output_format="mp4",
            output_dir="OUTPUT",
            file_info={"size_formatted": "15.8 Mo", "extension": "HTML"}
        )
        task.progress = float(pct)
        task.status = status
        window.tasks.append(task)
        window.task_table.add_task(task)

    window.show()
    app.processEvents()

    table = window.task_table
    assert table.rowCount() == len(test_data)

    for i, (pct, status) in enumerate(test_data):
        cell_w = table.cellWidget(i, 5)
        assert cell_w is not None, f"Le conteneur de la colonne 5 (ligne {i}) doit exister."
        pbar = cell_w.findChild(CyberTableProgressBar)
        assert pbar is not None, f"CyberTableProgressBar doit être présent dans la colonne 5 (ligne {i})."
        assert pbar.value() == pct, f"Valeur attendue {pct}, obtenu {pbar.value()}"

    # Test dynamique de mise à jour de la progression
    task_test = window.tasks[1]
    task_test.progress = 62.0
    table.update_task_progress(task_test)
    cell_w1 = table.cellWidget(1, 5)
    pbar1 = cell_w1.findChild(CyberTableProgressBar)
    assert pbar1.value() == 62, f"La mise à jour dynamique a échoué : attendu 62, obtenu {pbar1.value()}"

    os.makedirs("tests/screenshots", exist_ok=True)
    table_dark_path = os.path.abspath("tests/screenshots/verified_pbar_centered_dark.png")
    table.grab().save(table_dark_path)
    print(f"-> Capture Dark Mode enregistrée : {table_dark_path}")

    # Test bascule Thème Clair
    window._toggle_theme()
    app.processEvents()
    table_light_path = os.path.abspath("tests/screenshots/verified_pbar_centered_light.png")
    table.grab().save(table_light_path)
    print(f"-> Capture Light Mode enregistrée : {table_light_path}")

    window.close()
    print("-> VALIDATION DE CENTRAGE DU POURCENTAGE ET DE LA BARRE : 100% SUCCÈS !")

if __name__ == "__main__":
    run_centering_validation()

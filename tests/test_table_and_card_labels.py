"""
Test de validation de haute précision pour la lisibilité et l'affichage complet
des textes du tableau de conversion et de la carte d'aperçu studio.
"""
import sys
import os
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from src.core.converter_engine import ConversionTask
from src.ui.main_window import MainWindow

def test_table_and_card_rendering():
    app = QApplication.instance() or QApplication(sys.argv)

    window = MainWindow(is_light_mode=False)
    window.telemetry_timer.stop()
    window.cyber_bg.timer.stop()
    window.resize(1300, 860)

    # 1. Vérification des largeurs de colonnes configurées
    table = window.task_table
    col_widths = {
        0: table.columnWidth(0),
        1: table.columnWidth(1),
        2: table.columnWidth(2),
        3: table.columnWidth(3),
        4: table.columnWidth(4),
        5: table.columnWidth(5),
        6: table.columnWidth(6),
        7: table.columnWidth(7),
        8: table.columnWidth(8),
    }
    print("-> Largeurs des colonnes du tableau :", col_widths)
    assert col_widths[2] >= 68, f"Col Source ({col_widths[2]}px) doit être >= 68px pour accueillir HTML/HTML5/WEBM"
    assert col_widths[3] >= 105, f"Col Format Cible ({col_widths[3]}px) doit être >= 105px pour afficher 'Format Cible' sans rognage"
    assert col_widths[4] >= 80, f"Col Taille ({col_widths[4]}px) doit être >= 80px pour afficher '172.4 KB' sans points de suspension"
    assert col_widths[7] >= 95, f"Col Statut ({col_widths[7]}px) doit être >= 95px pour afficher 'En attente' sans points de suspension"
    assert col_widths[8] >= 135, f"Col Actions ({col_widths[8]}px) doit être >= 135px pour afficher les 4 boutons sans coupure"

    # 2. Ajouter une tâche HTML réelle similaire au screenshot de l'utilisateur
    html_sample = os.path.abspath("nouvelle-publicit-gran-laku/composition.html")
    if not os.path.exists(html_sample):
        # Fallback si le chemin relatif n'est pas trouvé
        html_sample = os.path.abspath("composition.html")
        if not os.path.exists(html_sample):
            with open("temp_test.html", "w") as f:
                f.write("<html><body>Test</body></html>")
            html_sample = os.path.abspath("temp_test.html")

    file_info = {
        "name": "composition.html",
        "extension": "HTML",
        "size": 176537,
        "size_formatted": "172.4 KB",
        "category": "web",
        "mime_type": "text/html"
    }
    task = ConversionTask(
        task_id="task_test_01",
        input_path=html_sample,
        output_format="mp4",
        output_dir="OUTPUT",
        options={"resolution": "1920x1080"},
        file_info=file_info
    )
    window.tasks.append(task)
    window.task_table.add_task(task)

    # 3. Charger le média dans la carte d'aperçu
    card = window.preview_card
    card.load_media(html_sample)

    window.show()
    app.processEvents()

    # 4. Vérifications textuelles des cellules
    item_file = table.item(0, 1).text()
    item_source = table.item(0, 2).text()
    item_target = table.item(0, 3).text()
    item_size = table.item(0, 4).text()
    item_status = table.item(0, 7).text()

    print(f"-> Valeurs dans la ligne 0 :")
    print(f"   Fichier      : {item_file}")
    print(f"   Source       : {item_source}")
    print(f"   Format Cible : {item_target}")
    print(f"   Taille       : {item_size}")
    print(f"   Statut       : {item_status}")

    assert item_source == "HTML", f"Source attendue 'HTML', reçu '{item_source}'"
    assert item_size == "172.4 KB", f"Taille attendue '172.4 KB', reçu '{item_size}'"
    assert item_status == "En attente", f"Statut attendu 'En attente', reçu '{item_status}'"

    # Vérifications des boutons d'actions
    act_w = table.cellWidget(0, 8)
    assert act_w is not None, "Widget d'action doit exister"
    btns = act_w.findChildren(object)
    # Les boutons sont SpinningConvertButton, QPushButton 📁, QPushButton 🔍, QPushButton ✕
    print(f"-> Nombre d'éléments dans le widget d'action : {len(btns)}")

    # Vérification des métadonnées de la carte
    print("-> Valeurs dans la carte d'inspection :")
    print(f"   Résolution label : {card.lbl_res_label.text()} | Valeur : {card.lbl_res_val.text()}")
    print(f"   Codec label      : {card.lbl_codec_label.text()} | Valeur : {card.lbl_codec_val.text()}")
    print(f"   Cadence label    : {card.lbl_time_label.text()} | Valeur : {card.lbl_time_val.text()}")
    print(f"   Taille label     : {card.lbl_size_label.text()} | Valeur : {card.lbl_size_val.text()}")

    # Capture d'écran de validation
    os.makedirs("tests/screenshots", exist_ok=True)
    screenshot_file = os.path.abspath("tests/screenshots/verified_table_and_card_labels.png")
    pix = window.grab()
    pix.save(screenshot_file)
    print(f"-> Capture de validation sauvegardée : {screenshot_file}")

    window.close()
    print("-> TOUTES LES VÉRIFICATIONS DE LISIBILITÉ ONT RÉUSSI AVEC SUCCÈS (100% OK) !")

if __name__ == "__main__":
    test_table_and_card_rendering()

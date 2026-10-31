"""
Tests unitaires pour le Système d'Internationalisation (i18n) en 8 Langues de GLC CONVERTER.
Éditeur: GRAN LAKU COMPANY
"""
import unittest
import os
import sys
from pathlib import Path

# Assurer l'inclusion de la racine du projet
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from src.core.i18n import I18nManager, tr, LANGUAGES, TRANSLATIONS, DEFAULT_LANGUAGE


class TestI18n8Languages(unittest.TestCase):
    """Vérifie le bon fonctionnement du moteur i18n et de toutes les langues."""

    @classmethod
    def setUpClass(cls):
        # Créer QApplication pour les widgets de test si nécessaire
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def setUp(self):
        self.i18n = I18nManager.get_instance()
        self.i18n.set_language("fr")

    def test_all_8_languages_present(self):
        """Vérifie la présence des 8 langues officielles de WASDEV."""
        required_codes = ["fr", "ht", "en", "es", "pt", "de", "it", "zh"]
        for code in required_codes:
            self.assertIn(code, LANGUAGES, f"Langue manquante dans LANGUAGES: {code}")
            self.assertIn(code, TRANSLATIONS, f"Dictionnaire manquant dans TRANSLATIONS: {code}")
            self.assertIn("name", LANGUAGES[code])
            self.assertIn("flag", LANGUAGES[code])

    def test_translations_keys_consistency(self):
        """Vérifie qu'aucune langue n'a de clés manquantes par rapport au Français."""
        fr_keys = set(TRANSLATIONS["fr"].keys())
        required_codes = ["fr", "ht", "en", "es", "pt", "de", "it", "zh"]
        for code in required_codes:
            lang_keys = set(TRANSLATIONS[code].keys())
            missing = fr_keys - lang_keys
            self.assertEqual(len(missing), 0, f"Clés manquantes pour {code}: {missing}")

    def test_runtime_language_switch(self):
        """Vérifie la bascule dynamique et la notification des écouteurs."""
        notifications = []

        def listener(code):
            notifications.append(code)

        self.i18n.register_listener(listener)

        # Basculer en Kreyòl Ayisyen
        self.i18n.set_language("ht")
        self.assertEqual(self.i18n.get_language(), "ht")
        self.assertEqual(notifications[-1], "ht")
        self.assertEqual(tr("step1_title"), "① ETAP 1 : CHWAZI MEDYA A")
        self.assertEqual(tr("btn_convert_all"), "🚀 TOUT KONVÈTI")

        # Basculer en English
        self.i18n.set_language("en")
        self.assertEqual(self.i18n.get_language(), "en")
        self.assertEqual(notifications[-1], "en")
        self.assertEqual(tr("step1_title"), "① STEP 1 : CHOOSE MEDIA")
        self.assertEqual(tr("btn_convert_all"), "🚀 CONVERT ALL")

        # Basculer en Español
        self.i18n.set_language("es")
        self.assertEqual(self.i18n.get_language(), "es")
        self.assertEqual(tr("step1_title"), "① PASO 1 : ELEGIR EL MEDIO")
        self.assertEqual(tr("btn_convert_all"), "🚀 CONVERTIR TODO")

        # Basculer en Português
        self.i18n.set_language("pt")
        self.assertEqual(tr("step1_title"), "① ETAPA 1 : ESCOLHER A MÍDIA")
        self.assertEqual(tr("btn_convert_all"), "🚀 CONVERTER TUDO")

        # Basculer en Deutsch
        self.i18n.set_language("de")
        self.assertEqual(tr("step1_title"), "① SCHRITT 1 : MEDIEN AUSWÄHLEN")
        self.assertEqual(tr("btn_convert_all"), "🚀 ALLES KONVERTIEREN")

        # Basculer en Italiano
        self.i18n.set_language("it")
        self.assertEqual(tr("step1_title"), "① PASSAGGIO 1 : SCEGLI IL MEDIA")
        self.assertEqual(tr("btn_convert_all"), "🚀 CONVERTI TUTTO")

        # Basculer en 中文 (Chinese)
        self.i18n.set_language("zh")
        self.assertEqual(tr("step1_title"), "① 第一步：选择媒体文件")
        self.assertEqual(tr("btn_convert_all"), "🚀 全部转换")

        # Retour en Français
        self.i18n.set_language("fr")
        self.assertEqual(tr("step1_title"), "① ÉTAPE 1 : CHOISIR LE MÉDIA")
        self.assertEqual(tr("btn_convert_all"), "🚀 TOUT CONVERTIR")

        self.i18n.unregister_listener(listener)

    def test_variable_interpolation(self):
        """Vérifie le formattage des variables dans les chaînes traduites."""
        self.i18n.set_language("fr")
        queue_fr = tr("status_queue", done=3, total=10)
        self.assertEqual(queue_fr, "File : 3/10 terminé(s)")

        self.i18n.set_language("ht")
        queue_ht = tr("status_queue", done=3, total=10)
        self.assertEqual(queue_ht, "Lis : 3/10 fini")

        self.i18n.set_language("en")
        queue_en = tr("status_queue", done=3, total=10)
        self.assertEqual(queue_en, "Queue : 3/10 completed")

    def test_ui_widgets_live_retranslation(self):
        """Vérifie que les composants UI réagissent tous instantanément au changement de langue."""
        from src.ui.main_window import MainWindow

        win = MainWindow(is_light_mode=False)

        # 1. En Français
        self.i18n.set_language("fr")
        self.assertEqual(win.drop_zone.lbl_step.text(), "① ÉTAPE 1 : CHOISIR LE MÉDIA")
        self.assertEqual(win.preset_panel.lbl_step.text(), "② ÉTAPE 2 : CHOISIR LE FORMAT CIBLE")
        self.assertEqual(win.lbl_step3.text(), "③ ÉTAPE 3 : CONVERTIR & SAUVER")
        self.assertEqual(win.btn_start.text(), "🚀 TOUT CONVERTIR")
        self.assertEqual(win.task_table.horizontalHeaderItem(1).text(), "Fichier")

        # 2. Bascule en Kreyòl Ayisyen
        self.i18n.set_language("ht")
        self.assertEqual(win.drop_zone.lbl_step.text(), "① ETAP 1 : CHWAZI MEDYA A")
        self.assertEqual(win.drop_zone.title_label.text(), "Glise fichye w yo la a")
        self.assertEqual(win.preset_panel.lbl_step.text(), "② ETAP 2 : CHWAZI FÒMA SIB LA")
        self.assertEqual(win.lbl_step3.text(), "③ ETAP 3 : KONVÈTI & SOVE")
        self.assertEqual(win.btn_start.text(), "🚀 TOUT KONVÈTI")
        self.assertEqual(win.task_table.horizontalHeaderItem(1).text(), "Fichye")

        # 3. Bascule en English
        self.i18n.set_language("en")
        self.assertEqual(win.drop_zone.lbl_step.text(), "① STEP 1 : CHOOSE MEDIA")
        self.assertEqual(win.preset_panel.lbl_step.text(), "② STEP 2 : CHOOSE TARGET FORMAT")
        self.assertEqual(win.lbl_step3.text(), "③ STEP 3 : CONVERT & SAVE")
        self.assertEqual(win.btn_start.text(), "🚀 CONVERT ALL")
        self.assertEqual(win.task_table.horizontalHeaderItem(1).text(), "File")

        # 4. Bascule en Español
        self.i18n.set_language("es")
        self.assertEqual(win.drop_zone.lbl_step.text(), "① PASO 1 : ELEGIR EL MEDIO")
        self.assertEqual(win.preset_panel.lbl_step.text(), "② PASO 2 : ELEGIR EL FORMATO DESTINO")
        self.assertEqual(win.lbl_step3.text(), "③ PASO 3 : CONVERTIR Y GUARDAR")
        self.assertEqual(win.btn_start.text(), "🚀 CONVERTIR TODO")
        self.assertEqual(win.task_table.horizontalHeaderItem(1).text(), "Archivo")

        # 5. Bascule en 简体中文
        self.i18n.set_language("zh")
        self.assertEqual(win.drop_zone.lbl_step.text(), "① 第一步：选择媒体文件")
        self.assertEqual(win.preset_panel.lbl_step.text(), "② 第二步：选择目标格式")
        self.assertEqual(win.lbl_step3.text(), "③ 第三步：转换并保存")
        self.assertEqual(win.btn_start.text(), "🚀 全部转换")
        self.assertEqual(win.task_table.horizontalHeaderItem(1).text(), "文件")

        # Rétablir la langue par défaut (Français)
        self.i18n.set_language("fr")
        win.close()


if __name__ == "__main__":
    unittest.main()

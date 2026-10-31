"""
GLC CONVERTER — Convertisseur Universel Ultime
Éditeur: GRAN LAKU COMPANY
Site Web Officiel: https://granlaku.com/glcconverter
"""
import sys
import os
import time
from pathlib import Path

RENDER_HTML_FLAG = "--glc-render-html"


def _run_html_renderer():
    """Moteur HTML → vidéo lancé en sous-processus par la version installée (html_video_engine.py)."""
    sys.argv = [a for a in sys.argv if a != RENDER_HTML_FLAG]
    if sys.stdout is None and sys.platform == "win32":
        # Exécutable sans console : récupère le tube stdout ouvert par le processus parent.
        try:
            import ctypes
            import msvcrt
            handle = ctypes.windll.kernel32.GetStdHandle(-11)
            fd = msvcrt.open_osfhandle(handle, os.O_WRONLY)
            sys.stdout = open(fd, "w", encoding="utf-8", buffering=1)
        except Exception:
            pass
    from src.core.html_video_renderer import main as render_main
    render_main()


if RENDER_HTML_FLAG in sys.argv:
    _run_html_renderer()
    sys.exit(0)

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QTimer

from src.config import APP_NAME, APP_VERSION, COMPANY_NAME, LOGO_PATH, ICON_PATH
from src.ui.theme import STUDIO_STYLE, get_theme_stylesheet
from src.ui.splash_screen import FuturisticSplashScreen
from src.ui.main_window import MainWindow

def main():
    # Configuration sécurisée pour QtWebEngine et multimédia
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--no-sandbox --disable-logging --disable-gpu-watchdog"
    try:
        import PySide6.QtWebEngineWidgets
    except ImportError:
        pass

    # Contexte OpenGL partagé (requis par QtWebEngine) : évite la recréation de la fenêtre native
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts, True)

    # Optimisation High-DPI
    if hasattr(Qt, "AA_EnableHighDpiScaling"):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, "AA_UseHighDpiPixmaps"):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName(COMPANY_NAME)

    # Définition de l'icône globale de l'application
    if ICON_PATH.exists():
        app.setWindowIcon(QIcon(str(ICON_PATH)))
    elif LOGO_PATH.exists():
        app.setWindowIcon(QIcon(str(LOGO_PATH)))

    # Détection du mode : Thème Clair par défaut (option --dark pour démarrer en Thème Sombre)
    is_light = "--dark" not in sys.argv
    app.setStyleSheet(get_theme_stylesheet(is_light))

    # Initialisation de la fenêtre principale (pré-chargée)
    window = MainWindow(is_light_mode=is_light)

    # N'afficher la fenêtre qu'une fois le lecteur Web prêt (max 5 s) : sinon le premier
    # ajout d'un fichier HTML force Qt à recréer la fenêtre native (elle « se ferme » puis revient).
    def show_when_ready(on_shown=None):
        deadline = time.monotonic() + 5.0

        def check():
            if window.preview_card.web_ready or time.monotonic() > deadline:
                if on_shown:
                    on_shown()
                window.show()
            else:
                QTimer.singleShot(50, check)

        check()

    # Gestion de l'option sans splash pour tests rapides
    if "--no-splash" in sys.argv:
        show_when_ready()
        sys.exit(app.exec())

    # Affichage du Splash Screen Futuriste Haute Technologie
    splash = FuturisticSplashScreen(is_light_mode=is_light)

    def on_loading_finished():
        show_when_ready(on_shown=splash.close)

    splash.loading_finished.connect(on_loading_finished)
    splash.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()

"""
GLC CONVERTER — Script d'Empaquetage & Build Windows Dist
Éditeur: GRAN LAKU COMPANY | https://granlaku.com/glcconverter

Ce script automatise la compilation de GLC CONVERTER en distribution Windows autonome
en respectant strictement les licences LGPL (mode répertoire dynamique avec DLLs séparées).
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"
MAIN_SCRIPT = PROJECT_ROOT / "main.py"
ICON_PATH = PROJECT_ROOT / "LOGO" / "glc_icon.ico"
LOGO_DIR = PROJECT_ROOT / "LOGO"

def build():
    print(f"=== Compilation de GLC CONVERTER pour Windows ===")
    print(f"Racine du projet : {PROJECT_ROOT}")

    # Vérification des licences au préalable
    check_script = PROJECT_ROOT / "tools" / "check_licenses.py"
    if check_script.exists():
        print("Vérification des licences...")
        ret = subprocess.run([sys.executable, str(check_script)], cwd=str(PROJECT_ROOT))
        if ret.returncode != 0:
            print("ERREUR : Problème de licence détecté. Annulation du build.")
            return False

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=GLC CONVERTER",
        "--onedir",
        "--windowed",
        f"--icon={ICON_PATH}",
        f"--add-data={LOGO_DIR};LOGO",
        f"--add-data={PROJECT_ROOT / 'src' / 'ui' / 'icons'};src/ui/icons",
        f"--add-data={PROJECT_ROOT / 'LICENSE.txt'};.",
        f"--add-data={PROJECT_ROOT / 'THIRD_PARTY_NOTICES.md'};.",
        f"--add-data={PROJECT_ROOT / 'settings.example.json'};.",
        "--clean",
        "--noconfirm",
        str(MAIN_SCRIPT)
    ]

    print(f"Exécution de PyInstaller...")
    ret = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
    if ret.returncode == 0:
        print("\nSUCCÈS : Distribution Windows créée dans dist/GLC CONVERTER/")
        return True
    else:
        print(f"\nÉCHEC de PyInstaller avec code {ret.returncode}")
        return False

if __name__ == "__main__":
    success = build()
    sys.exit(0 if success else 1)

"""
GLC CONVERTER — Générateur de l'installateur Windows (.msi)
Éditeur: GRAN LAKU COMPANY | https://granlaku.com/glcconverter

Empaquette dist/GLC CONVERTER/ (produit par tools/build_windows_dist.py) dans
dist/GLC-Converter-v<VERSION>-x64.msi :
- installation par machine dans C:\\Program Files\\GRAN LAKU COMPANY\\GLC CONVERTER
- raccourcis Bureau et Menu Démarrer, icône dans « Applications installées »
- mise à jour majeure : une version plus ancienne est désinstallée automatiquement
Le paquet ne contient que les métadonnées de l'entreprise, aucune donnée personnelle.
"""
import sys
import uuid
from pathlib import Path

import msilib
from msilib import schema, sequence, text, Directory, Feature, CAB

PROJECT_ROOT = Path(__file__).resolve().parent.parent
APP_DIR = PROJECT_ROOT / "dist" / "GLC CONVERTER"
ICON_PATH = PROJECT_ROOT / "LOGO" / "glc_icon.ico"

PRODUCT_NAME = "GLC CONVERTER"
MANUFACTURER = "GRAN LAKU COMPANY"
VERSION = "1.0.0"
EXE_NAME = "GLC CONVERTER.exe"
WEBSITE = "https://granlaku.com/glcconverter"
OUTPUT_MSI = PROJECT_ROOT / "dist" / f"GLC-Converter-v{VERSION}-x64.msi"

# Ne jamais changer : relie toutes les versions entre elles pour les mises à jour.
UPGRADE_CODE = "{B7A4C120-6E11-4A55-9C88-1234567890AB}"
# Identifiants stables par version (même build → mêmes GUID)
_NS = uuid.UUID(UPGRADE_CODE.strip("{}"))
PRODUCT_CODE = "{%s}" % str(uuid.uuid5(_NS, f"product:{VERSION}")).upper()


def _component_uuid(rel_dir: str) -> str:
    return "{%s}" % str(uuid.uuid5(_NS, f"component:{VERSION}:{rel_dir}")).upper()


def _add_tree(db, cab, parent: Directory, src: Path, counter: list):
    """Ajoute récursivement les sous-dossiers et fichiers de src sous parent."""
    for entry in sorted(src.iterdir(), key=lambda p: p.name.lower()):
        if entry.is_dir():
            counter[0] += 1
            logical = f"d{counter[0]}"
            default = f"{parent.make_short(entry.name)}|{entry.name}"
            sub = Directory(db, cab, parent, entry.name, logical, default)
            files = [f for f in entry.iterdir() if f.is_file()]
            if files:
                rel = entry.relative_to(APP_DIR).as_posix()
                sub.start_component(logical, flags=0, uuid=_component_uuid(rel))
                for f in sorted(files, key=lambda p: p.name.lower()):
                    sub.add_file(f.name)
            _add_tree(db, cab, sub, entry, counter)


def create_msi_package() -> Path:
    if not (APP_DIR / EXE_NAME).exists():
        raise SystemExit(f"Introuvable : {APP_DIR / EXE_NAME}\nLancez d'abord : python tools/build_windows_dist.py")

    print(f"=== {PRODUCT_NAME} v{VERSION} — {MANUFACTURER} ===")
    OUTPUT_MSI.unlink(missing_ok=True)

    db = msilib.init_database(str(OUTPUT_MSI), schema, PRODUCT_NAME, PRODUCT_CODE, VERSION, MANUFACTURER)
    msilib.add_tables(db, sequence)
    msilib.add_data(db, "ActionText", text.ActionText)
    msilib.add_data(db, "UIText", text.UIText)

    # Résumé du paquet (Propriétés du fichier .msi)
    si = db.GetSummaryInformation(20)
    si.SetProperty(msilib.PID_TITLE, f"{PRODUCT_NAME} {VERSION} Installer")
    si.SetProperty(msilib.PID_SUBJECT, PRODUCT_NAME)
    si.SetProperty(msilib.PID_AUTHOR, MANUFACTURER)
    si.SetProperty(msilib.PID_KEYWORDS, "converter, video, audio, image, html, open source")
    # Textes du paquet en ASCII : la base MSI n'a pas de page de code Unicode
    si.SetProperty(msilib.PID_COMMENTS, f"{PRODUCT_NAME} - {WEBSITE} - MIT License")
    si.SetProperty(msilib.PID_APPNAME, f"{MANUFACTURER} build tools")
    si.Persist()

    msilib.add_data(db, "Property", [
        ("UpgradeCode", UPGRADE_CODE),
        ("ALLUSERS", "1"),
        ("ARPHELPLINK", WEBSITE),
        ("ARPURLINFOABOUT", WEBSITE),
        ("ARPCOMMENTS", "Universal media converter - MIT License"),
        ("ARPPRODUCTICON", "glc_icon.ico"),
        ("ARPNOMODIFY", "1"),
        ("SecureCustomProperties", "OLDERFOUND;NEWERFOUND"),
    ])
    msilib.add_data(db, "Icon", [("glc_icon.ico", msilib.Binary(str(ICON_PATH)))])

    # Mise à jour majeure : retirer les versions plus anciennes, refuser de remplacer une plus récente
    msilib.add_data(db, "Upgrade", [
        (UPGRADE_CODE, None, VERSION, None, 1, None, "OLDERFOUND"),
        (UPGRADE_CODE, VERSION, None, None, 2, None, "NEWERFOUND"),
    ])
    msilib.add_data(db, "LaunchCondition", [
        ("NOT NEWERFOUND", f"A newer version of {PRODUCT_NAME} is already installed."),
    ])
    existing = {row[0] for row in sequence.InstallExecuteSequence}
    if "RemoveExistingProducts" not in existing:
        msilib.add_data(db, "InstallExecuteSequence", [("RemoveExistingProducts", None, 1450)])

    # Arborescence : TARGETDIR > ProgramFiles64Folder > GRAN LAKU COMPANY > GLC CONVERTER
    cab = CAB("glc")
    root = Directory(db, cab, None, str(APP_DIR), "TARGETDIR", "SourceDir")
    feature = Feature(db, "Complete", PRODUCT_NAME, f"{PRODUCT_NAME} application files", 1, directory="INSTALLDIR")
    feature.set_current()
    pf = Directory(db, cab, root, ".", "ProgramFiles64Folder", ".")
    company = Directory(db, cab, pf, ".", "COMPANYDIR", f"{pf.make_short(MANUFACTURER)}|{MANUFACTURER}")
    install = Directory(db, cab, company, ".", "INSTALLDIR", f"{company.make_short(PRODUCT_NAME)}|{PRODUCT_NAME}")

    install.start_component("MainExecutable", flags=0, keyfile=EXE_NAME, uuid=_component_uuid("."))
    exe_key = None
    for f in sorted(APP_DIR.iterdir(), key=lambda p: p.name.lower()):
        if f.is_file():
            key = install.add_file(f.name)
            if f.name == EXE_NAME:
                exe_key = key

    counter = [0]
    _add_tree(db, cab, install, APP_DIR, counter)

    msilib.add_data(db, "Directory", [
        ("DesktopFolder", "TARGETDIR", "."),
        ("ProgramMenuFolder", "TARGETDIR", "."),
    ])
    shortcut_name = f"GLCCONV|{PRODUCT_NAME}"
    msilib.add_data(db, "Shortcut", [
        ("DesktopShortcut", "DesktopFolder", shortcut_name, "MainExecutable",
         f"[#{exe_key}]", None, "Universal media converter", None, "glc_icon.ico", 0, None, "INSTALLDIR"),
        ("StartMenuShortcut", "ProgramMenuFolder", shortcut_name, "MainExecutable",
         f"[#{exe_key}]", None, "Universal media converter", None, "glc_icon.ico", 0, None, "INSTALLDIR"),
    ])

    print("Compression des fichiers (cela peut prendre quelques minutes)...")
    cab.commit(db)
    db.Commit()

    size_mb = OUTPUT_MSI.stat().st_size / (1024 * 1024)
    print(f"[OK] {counter[0]} sous-dossiers, installateur : {OUTPUT_MSI.name} ({size_mb:.1f} Mo)")
    return OUTPUT_MSI


if __name__ == "__main__":
    out = create_msi_package()
    sys.exit(0 if out.exists() else 1)

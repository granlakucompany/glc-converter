"""
GLC CONVERTER — Vérification des licences avant empaquetage
Éditeur: GRAN LAKU COMPANY | https://granlaku.com/glcconverter

GLC CONVERTER est distribué sous licence MIT. Aucune bibliothèque livrée avec lui
ne doit contenir de composant GPL (x264, x265, xvid, libpostproc…), sinon l'installateur
tomberait sous la GPL et ne pourrait plus être distribué sous MIT.

Usage : python tools/check_licenses.py
Code de sortie 0 = livrable ; 1 = problème de licence à corriger avant de livrer.
"""
import importlib
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Bibliothèques natives sous GPL ou non redistribuables.
FORBIDDEN_NATIVE = ("libx264", "libx265", "libxvidcore", "libxavs", "libfdk-aac", "postproc")

# Paquets Python livrés avec l'application (ceux que le code importe).
SHIPPED_PACKAGES = (
    "av", "PySide6", "PIL", "pi_heif", "pillow_avif", "pypdfium2", "rawpy",
    "cairosvg", "reportlab", "docx", "numpy", "psutil",
)

# Paquets qui ne doivent pas être importés par le code (ils embarquent du GPL).
FORBIDDEN_IMPORTS = ("pillow_heif",)


def _native_files(package_dir: Path):
    """DLL / modules natifs du paquet et de son dossier « <paquet>.libs » (delvewheel)."""
    roots = [package_dir, package_dir.parent / f"{package_dir.name}.libs"]
    for root in roots:
        if root.is_dir():
            for path in root.rglob("*"):
                if path.suffix.lower() in (".dll", ".pyd", ".so"):
                    yield path


def check_shipped_packages():
    problems = []
    for name in SHIPPED_PACKAGES:
        try:
            module = importlib.import_module(name)
        except Exception:
            continue
        package_dir = Path(module.__file__).resolve().parent
        for path in _native_files(package_dir):
            low = path.name.lower()
            if any(low.startswith(bad) or f"-{bad}" in low or f"_{bad}" in low for bad in FORBIDDEN_NATIVE):
                problems.append(f"{name} : bibliothèque GPL livrée → {path}")
    return problems


def check_ffmpeg():
    problems = []
    try:
        import av
        from av import _core
    except Exception as exc:
        return [f"PyAV introuvable : {exc}"]
    for lib, meta in getattr(_core, "library_meta", {}).items():
        license_text = str(meta.get("license", "")) if isinstance(meta, dict) else ""
        if "GPL" in license_text and "LGPL" not in license_text:
            problems.append(f"FFmpeg {lib} compilé sous GPL : {license_text}")
        configuration = str(meta.get("configuration", "")) if isinstance(meta, dict) else ""
        for flag in ("--enable-gpl", "--enable-nonfree", "--enable-libx264", "--enable-libx265"):
            if flag in configuration and f"FFmpeg configuré avec {flag}" not in problems:
                problems.append(f"FFmpeg configuré avec {flag}")
    for encoder in ("libx264", "libx265", "libxvid"):
        if encoder in av.codec.codecs_available:
            problems.append(f"Encodeur GPL disponible dans FFmpeg : {encoder}")
    return problems


def check_source_imports():
    problems = []
    pattern = re.compile(r"^\s*(?:import|from)\s+(" + "|".join(FORBIDDEN_IMPORTS) + r")\b", re.MULTILINE)
    for path in list((PROJECT_ROOT / "src").rglob("*.py")) + [PROJECT_ROOT / "main.py"]:
        if path.exists() and pattern.search(path.read_text(encoding="utf-8", errors="ignore")):
            problems.append(f"Import interdit (embarque du GPL) dans {path.relative_to(PROJECT_ROOT)}")
    return problems


def run_checks():
    return check_source_imports() + check_ffmpeg() + check_shipped_packages()


def main() -> int:
    problems = run_checks()
    if problems:
        print("ÉCHEC — composants incompatibles avec une vente en logiciel fermé :")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print("OK — aucune dépendance livrée ne contient de composant GPL.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""
GLC CONVERTER — Configuration et Métadonnées Officielles
Éditeur: GRAN LAKU COMPANY
Site Web: https://granlaku.com/glcconverter
"""
import os
import sys
from pathlib import Path

# Informations de l'application & Entreprise
APP_NAME = "GLC CONVERTER"
APP_SUBTITLE = "Convertisseur Universel de Nouvelle Génération"
APP_VERSION = "1.0.0 Pro Studio Edition"
COMPANY_NAME = "GRAN LAKU COMPANY"
COMPANY_WEBSITE = "https://granlaku.com/glcconverter"
COMPANY_SUPPORT_EMAIL = "support@granlaku.com"
COPYRIGHT_TEXT = "© 2026 GRAN LAKU COMPANY. Open source · MIT License."
GITHUB_URL = "https://github.com/granlakucompany/glc-converter"

# Répertoires clés
ROOT_DIR = Path(__file__).resolve().parent.parent
LOGO_DIR = ROOT_DIR / "LOGO"
DOCS_DIR = ROOT_DIR / "DOCS"


def _default_output_dir() -> Path:
    """OUTPUT/ à côté du code en développement ; Documents/GLC CONVERTER/OUTPUT une fois installé
    (le dossier d'installation, ex. C:\\Program Files, n'est pas accessible en écriture)."""
    if not getattr(sys, "frozen", False):
        local = ROOT_DIR / "OUTPUT"
        try:
            local.mkdir(exist_ok=True)
            return local
        except OSError:
            pass
    return Path.home() / "Documents" / APP_NAME / "OUTPUT"


OUTPUT_DIR = _default_output_dir()

# Fichiers de logo et bannières
LOGO_PATH = LOGO_DIR / "glc_logo.png"
LOGO_512_PATH = LOGO_DIR / "glc_logo_512.png"
LOGO_256_PATH = LOGO_DIR / "glc_logo_256.png"
LOGO_128_PATH = LOGO_DIR / "glc_logo_128.png"
LOGO_64_PATH = LOGO_DIR / "glc_logo_64.png"
LOGO_32_PATH = LOGO_DIR / "glc_logo_32.png"
LOGO_FULL_PATH = LOGO_DIR / "glc_converter_full_logo.png"
LOGO_FULL_LIGHT_PATH = LOGO_DIR / "glc_converter_full_logo_light.png"
LOGO_FULL_DARK_PATH = LOGO_DIR / "glc_converter_full_logo_dark.png"
LOGO_BANNER_DARK_PATH = LOGO_DIR / "glc_converter_banner_dark.png"
LOGO_BANNER_LIGHT_PATH = LOGO_DIR / "glc_converter_banner_light.png"
ICON_PATH = LOGO_DIR / "glc_icon.ico"

# Création automatique du dossier de sortie par défaut
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Formats supportés par catégorie
VIDEO_FORMATS = [
    "mp4", "mkv", "mov", "webm", "avi", "flv", "wmv", "ts", "m2ts", 
    "m4v", "vob", "3gp", "mxf", "prores"
]

IMAGE_FORMATS = [
    "png", "jpg", "jpeg", "webp", "avif", "heic", "heif", "tiff", 
    "bmp", "gif", "svg", "ico", "tga", "psd", "dng", "cr2", "nef"
]

AUDIO_FORMATS = [
    "mp3", "wav", "flac", "aac", "ogg", "opus", "m4a", "wma", "aiff", "alac"
]

DOCUMENT_FORMATS = [
    "pdf", "docx", "pptx", "xlsx", "txt", "md", "rtf", "epub", "html"
]

WEB_ANIMATION_FORMATS = [
    "html", "htm"
]

# Préréglages par défaut
DEFAULT_VIDEO_PRESET = {
    "format": "mp4",
    "video_codec": "h264",
    "audio_codec": "aac",
    "crf": 22,
    "bitrate": "4M",
    "resolution": "original",
    "fps": "original",
    "hw_accel": True
}

DEFAULT_AUDIO_PRESET = {
    "format": "mp3",
    "codec": "mp3",
    "bitrate": "320k",
    "sample_rate": 44100,
    "channels": 2
}

DEFAULT_IMAGE_PRESET = {
    "format": "webp",
    "quality": 85,
    "lossless": False,
    "resolution": "original"
}

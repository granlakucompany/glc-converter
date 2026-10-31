"""
GLC CONVERTER — Gestionnaire de Paramètres et Persistance (SettingsManager)
Éditeur: GRAN LAKU COMPANY | https://granlaku.com/glcconverter

Ce module gère la mémorisation et la persistance en temps réel de :
- Le dernier emplacement où un fichier a été ouvert (last_open_dir)
- Le dossier de destination personnalisé des conversions (last_output_dir)
- La synchronisation bidirectionnelle via QSettings (Registre Windows) et settings.json
"""
import os
import json
from pathlib import Path
from typing import Optional, Union, Any

from PySide6.QtCore import QSettings
from ..config import ROOT_DIR, OUTPUT_DIR, APP_NAME, COMPANY_NAME

# Chemins de persistance
CONFIG_DIR = Path.home() / ".glc_converter"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
PRIMARY_SETTINGS_JSON = CONFIG_DIR / "settings.json"
LOCAL_SETTINGS_JSON = ROOT_DIR / "settings.json"


class SettingsManager:
    """Gestionnaire centralisé pour la persistance des préférences utilisateur et derniers répertoires."""

    _instance: Optional["SettingsManager"] = None

    def __init__(self):
        self._qsettings = QSettings(COMPANY_NAME, APP_NAME)
        self._cache = {
            "last_open_dir": "",
            "last_output_dir": ""
        }
        self._load_settings()

    @classmethod
    def get_instance(cls) -> "SettingsManager":
        """Retourne l'instance singleton du gestionnaire de paramètres."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_settings(self):
        """Charge les paramètres depuis QSettings avec secours sur settings.json."""
        # 1. Tentative depuis QSettings
        saved_open_dir = self._qsettings.value("last_open_dir", "")
        saved_output_dir = self._qsettings.value("last_output_dir", "")

        # 2. Secours depuis le fichier JSON si QSettings est vide
        json_file = PRIMARY_SETTINGS_JSON if PRIMARY_SETTINGS_JSON.exists() else LOCAL_SETTINGS_JSON
        if json_file.exists():
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for k, v in data.items():
                        if k not in self._cache or not self._cache[k]:
                            self._cache[k] = v
                    if not saved_open_dir:
                        saved_open_dir = data.get("last_open_dir", "")
                    if not saved_output_dir:
                        saved_output_dir = data.get("last_output_dir", "")
            except Exception:
                pass

        self._cache["last_open_dir"] = str(saved_open_dir) if saved_open_dir else ""
        self._cache["last_output_dir"] = str(saved_output_dir) if saved_output_dir else ""

    def _save_settings(self):
        """Enregistre immédiatement les paramètres dans QSettings et dans les fichiers JSON."""
        # Sauvegarde QSettings
        try:
            for k, v in self._cache.items():
                self._qsettings.setValue(k, v)
            self._qsettings.sync()
        except Exception:
            pass

        # Sauvegarde JSON miroir
        data = dict(self._cache)
        for target in [PRIMARY_SETTINGS_JSON, LOCAL_SETTINGS_JSON]:
            try:
                target.parent.mkdir(parents=True, exist_ok=True)
                with open(target, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
            except Exception:
                pass

    def get_value(self, key: str, default: Any = None) -> Any:
        """Récupère une valeur générique depuis le cache / persistance."""
        return self._cache.get(key, default)

    def set_value(self, key: str, value: Any):
        """Définit et sauvegarde immédiatement une valeur générique."""
        self._cache[key] = value
        self._save_settings()

    def get_last_open_dir(self) -> str:
        """
        Retourne le dernier répertoire où un fichier a été ouvert.
        Vérifie la validité du chemin ; s'il n'existe plus, bascule sur Mes Documents.
        """
        raw_dir = self._cache.get("last_open_dir", "").strip()
        if raw_dir and os.path.isdir(raw_dir):
            return str(Path(raw_dir).resolve())

        # Fallback 1: Dossier Documents de l'utilisateur
        docs = Path.home() / "Documents"
        if docs.is_dir():
            return str(docs.resolve())

        # Fallback 2: Répertoire personnel de l'utilisateur
        return str(Path.home().resolve())

    def set_last_open_dir(self, path_or_dir: Union[str, Path]) -> str:
        """
        Mémorise le dernier emplacement où un fichier a été ouvert.
        Si un fichier est fourni, extrait son répertoire parent.
        """
        if not path_or_dir:
            return self.get_last_open_dir()

        p = Path(path_or_dir).resolve()
        target_dir = p.parent if p.is_file() else p

        if target_dir.is_dir():
            resolved = str(target_dir)
            self._cache["last_open_dir"] = resolved
            self._save_settings()
            return resolved

        return self.get_last_open_dir()

    def get_output_dir(self) -> str:
        """Retourne le dossier de sortie mémorisé ou le dossier par défaut OUTPUT."""
        raw_dir = self._cache.get("last_output_dir", "").strip()
        if raw_dir and os.path.isdir(raw_dir):
            return str(Path(raw_dir).resolve())

        return str(OUTPUT_DIR.resolve())

    def set_output_dir(self, directory: Union[str, Path]) -> str:
        """Mémorise le dossier de destination des conversions."""
        p = Path(directory).resolve()
        p.mkdir(parents=True, exist_ok=True)
        resolved = str(p)
        self._cache["last_output_dir"] = resolved
        self._save_settings()
        return resolved


# Fonctions d'accès rapide direct
def get_last_open_dir() -> str:
    """Retourne le dernier répertoire d'ouverture mémorisé."""
    return SettingsManager.get_instance().get_last_open_dir()

def set_last_open_dir(path_or_dir: Union[str, Path]) -> str:
    """Met à jour et persiste le dernier répertoire où un fichier a été ouvert."""
    return SettingsManager.get_instance().set_last_open_dir(path_or_dir)

def get_output_dir() -> str:
    """Retourne le dossier de sortie mémorisé."""
    return SettingsManager.get_instance().get_output_dir()

def set_output_dir(directory: Union[str, Path]) -> str:
    """Met à jour et persiste le dossier de sortie."""
    return SettingsManager.get_instance().set_output_dir(directory)

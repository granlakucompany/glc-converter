"""
GLC CONVERTER — Détecteur Binaire Universel (Magic Bytes & Métadonnées)
Éditeur: GRAN LAKU COMPANY | https://granlaku.com/glcconverter
"""
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
import av
from PIL import Image

# Déverrouiller la limite pour inspecter les images 8K, 12K et au-delà
Image.MAX_IMAGE_PIXELS = None

class MimeDetector:
    """Détecte le type MIME réel d'un fichier via ses octets magiques d'en-tête."""
    
    MAGIC_SIGNATURES = {
        # Vidéo et Conteneurs
        b"\x00\x00\x00\x18ftypmp42": ("video/mp4", "mp4"),
        b"\x00\x00\x00\x20ftypisom": ("video/mp4", "mp4"),
        b"\x00\x00\x00\x14ftypqt  ": ("video/quicktime", "mov"),
        b"\x1a\x45\xdf\xa3": ("video/x-matroska", "mkv"), # Matroska / WebM
        b"RIFF....AVI ": ("video/x-msvideo", "avi"),
        b"FLV\x01": ("video/x-flv", "flv"),
        b"\x47": ("video/mp2t", "ts"),
        
        # Audio
        b"ID3": ("audio/mpeg", "mp3"),
        b"\xff\xfb": ("audio/mpeg", "mp3"),
        b"\xff\xf3": ("audio/mpeg", "mp3"),
        b"fLaC": ("audio/flac", "flac"),
        b"OggS": ("audio/ogg", "ogg"),
        b"RIFF....WAVE": ("audio/wav", "wav"),
        b"MThd": ("audio/midi", "midi"),
        
        # Images
        b"\x89PNG\r\n\x1a\n": ("image/png", "png"),
        b"\xff\xd8\xff": ("image/jpeg", "jpg"),
        b"RIFF....WEBP": ("image/webp", "webp"),
        b"GIF87a": ("image/gif", "gif"),
        b"GIF89a": ("image/gif", "gif"),
        b"BM": ("image/bmp", "bmp"),
        b"II*\x00": ("image/tiff", "tiff"),
        b"MM\x00*": ("image/tiff", "tiff"),
        b"8BPS": ("image/vnd.adobe.photoshop", "psd"),
        
        # Documents
        b"%PDF-": ("application/pdf", "pdf"),
        b"PK\x03\x04": ("application/zip", "zip_archive"), # docx, xlsx, pptx, epub
        b"{\\rtf": ("application/rtf", "rtf"),
    }

    @classmethod
    def identify_file(cls, filepath: str) -> Dict[str, Any]:
        """Analyse le fichier et retourne son profil détaillé."""
        s_fp = str(filepath).strip()

        # Prise en charge universelle des liens web et serveurs locaux (ex: http://localhost:3000, https://...)
        if s_fp.startswith("http://") or s_fp.startswith("https://"):
            from urllib.parse import urlparse
            parsed = urlparse(s_fp)
            name = (parsed.netloc + (parsed.path if parsed.path not in ["", "/"] else "")) or s_fp
            return {
                "path": s_fp,
                "filename": name,
                "name": name,
                "extension": "html",
                "size_bytes": 0,
                "size_formatted": "URL Web",
                "mime_type": "text/html",
                "category": "web",
                "metadata": {
                    "width": 1920,
                    "height": 1080,
                    "duration": 5.0,
                    "fps": 30,
                    "is_url": True,
                    "url": s_fp
                },
                "valid": True,
                "is_url": True,
                "details": f"Lien Web / Animation ({parsed.scheme}://{parsed.netloc})"
            }

        # Prise en charge des liens de fichiers locaux file://
        if s_fp.startswith("file://"):
            from PySide6.QtCore import QUrl
            local_p = QUrl(s_fp).toLocalFile()
            if local_p and Path(local_p).exists():
                filepath = local_p

        p = Path(filepath)
        if not p.exists():
            return {"error": "Fichier introuvable", "valid": False}
        
        size_bytes = p.stat().st_size
        ext = p.suffix.lower().lstrip(".")
        header = b""
        
        try:
            with open(p, "rb") as f:
                header = f.read(64)
        except Exception:
            pass

        detected_type = "unknown"
        detected_category = "other"
        
        # Recherche par magic bytes
        for sig, (mime, guessed_ext) in cls.MAGIC_SIGNATURES.items():
            if b"...." in sig:
                prefix, suffix = sig.split(b"....")
                if header.startswith(prefix) and suffix in header[:16]:
                    detected_type = mime
                    break
            elif header.startswith(sig):
                detected_type = mime
                break

        # Catégorisation intelligente complète selon le Plan
        if detected_type.startswith("video/") or ext in [
            "mp4", "mkv", "mov", "webm", "avi", "flv", "wmv", "ts", "m2ts", "mxf", "prores", "dnxhd"
        ]:
            detected_category = "video"
            if detected_type == "unknown":
                detected_type = f"video/{ext}"

        elif detected_type.startswith("audio/") or ext in [
            "mp3", "wav", "flac", "aac", "ogg", "opus", "m4a", "alac", "aiff", "ac3", "dts", "wma", "midi"
        ]:
            detected_category = "audio"
            if detected_type == "unknown":
                detected_type = f"audio/{ext}"

        elif detected_type.startswith("image/") or ext in [
            "png", "jpg", "jpeg", "webp", "avif", "heic", "tiff", "bmp", "tga", "qoi", "jxl",
            "psd", "psb", "exr", "hdr", "svg", "eps", "ai", "dng", "cr2", "nef", "arw", "ico"
        ]:
            detected_category = "image"
            if detected_type == "unknown":
                detected_type = f"image/{ext}"

        elif ext in ["obj", "stl", "gltf", "glb", "fbx", "ply"]:
            detected_category = "3d"
            detected_type = f"model/{ext}"

        elif ext in ["html", "htm", "xml", "xhtml"]:
            detected_category = "web"
            detected_type = "text/xml" if ext in ["xml", "xhtml"] else "text/html"

        elif ext == "json":
            # Vérifier si animation Lottie
            is_lottie = False
            try:
                with open(p, "r", encoding="utf-8", errors="ignore") as jf:
                    data = json.load(jf)
                    if isinstance(data, dict) and ("v" in data or "layers" in data):
                        is_lottie = True
            except Exception:
                pass
            if is_lottie:
                detected_category = "web"
                detected_type = "application/lottie+json"
            else:
                detected_category = "document"
                detected_type = "application/json"

        elif detected_type == "application/pdf" or ext in [
            "pdf", "docx", "pptx", "xlsx", "txt", "md", "rtf", "epub", "mobi"
        ]:
            detected_category = "document"
            if detected_type == "unknown":
                detected_type = f"application/{ext}"

        # Métadonnées détaillées
        metadata = cls._extract_metadata(str(p), detected_category)

        return {
            "path": str(p),
            "filename": p.name,
            "extension": ext,
            "size_bytes": size_bytes,
            "size_formatted": cls._format_size(size_bytes),
            "mime_type": detected_type,
            "category": detected_category,
            "metadata": metadata,
            "valid": True
        }

    @classmethod
    def _extract_metadata(cls, filepath: str, category: str) -> Dict[str, Any]:
        meta = {}
        if category in ["video", "audio"]:
            try:
                with av.open(filepath) as container:
                    if container.duration:
                        duration_sec = float(container.duration) / av.time_base
                        meta["duration"] = duration_sec
                        meta["duration_formatted"] = cls._format_duration(duration_sec)
                    
                    if container.streams.video:
                        vstream = container.streams.video[0]
                        meta["width"] = vstream.codec_context.width
                        meta["height"] = vstream.codec_context.height
                        meta["video_codec"] = vstream.codec_context.name
                        meta["fps"] = float(vstream.average_rate) if vstream.average_rate else 0
                    
                    if container.streams.audio:
                        astream = container.streams.audio[0]
                        meta["audio_codec"] = astream.codec_context.name
                        meta["sample_rate"] = astream.codec_context.sample_rate
                        meta["channels"] = astream.codec_context.channels
            except Exception:
                pass
        elif category == "image":
            try:
                with Image.open(filepath) as img:
                    meta["width"] = img.width
                    meta["height"] = img.height
                    meta["format"] = img.format
                    meta["mode"] = img.mode
            except Exception:
                pass
        elif category == "3d":
            p = Path(filepath)
            meta["format"] = p.suffix.upper().lstrip(".")
        return meta

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        for unit in ["B", "Ko", "Mo", "Go"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} To"

    @staticmethod
    def _format_duration(seconds: float) -> str:
        m, s = divmod(int(seconds), 60)
        h, m = divmod(m, 60)
        if h > 0:
            return f"{h:02d}:{m:02d}:{s:02d}"
        return f"{m:02d}:{s:02d}"

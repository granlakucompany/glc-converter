"""
GLC CONVERTER — Moteur Image Universel (Raster, Vectoriel, Next-Gen jusqu'en 12K)
Éditeur: GRAN LAKU COMPANY | https://granlaku.com/glcconverter
"""
import os
from pathlib import Path
from typing import Optional, Callable
from PIL import Image
import pillow_avif

# Déverrouiller la limite de pixels pour supporter le 8K, 12K et 16K sans blocage
Image.MAX_IMAGE_PIXELS = None

# Lecture HEIC / HEIF via pi-heif : version de pillow-heif sans encodeur x265 (GPL),
# donc compatible avec la distribution sous licence MIT. L'écriture HEIC n'est pas proposée.
try:
    from pi_heif import register_heif_opener
    register_heif_opener()
    HEIF_AVAILABLE = True
except Exception:
    HEIF_AVAILABLE = False

try:
    import cairosvg
    CAIROSVG_AVAILABLE = True
except Exception:
    CAIROSVG_AVAILABLE = False

try:
    import rawpy
    RAWPY_AVAILABLE = True
except Exception:
    RAWPY_AVAILABLE = False

class ImageEngine:
    """Convertit toutes les catégories d'images jusqu'à la résolution Ultra-HD 12K."""

    RAW_EXTENSIONS = {"cr2", "cr3", "nef", "arw", "dng", "orf", "rw2", "pef"}

    @classmethod
    def convert_image(
        cls,
        input_path: str,
        output_path: str,
        quality: int = 90,
        resolution: Optional[str] = None, # ex: "12288x6480", "7680x4320", "3840x2160"
        progress_callback: Optional[Callable[[float, float, str], None]] = None
    ) -> bool:
        """Convertit l'image source vers le format de sortie désiré avec support 12K."""
        in_p = Path(input_path)
        out_p = Path(output_path)
        ext_in = in_p.suffix.lower().lstrip(".")
        ext_out = out_p.suffix.lower().lstrip(".")

        if progress_callback:
            progress_callback(10.0, 0.0, "--:--")

        # Cas 1: Image source vectorielle SVG / EPS / AI
        if ext_in in ["svg"] and CAIROSVG_AVAILABLE and ext_out in ["png", "jpg", "jpeg", "webp", "pdf"]:
            kwargs = {}
            if resolution and "x" in resolution:
                try:
                    rw, rh = resolution.lower().split("x")
                    kwargs["output_width"] = int(rw)
                    kwargs["output_height"] = int(rh)
                except Exception:
                    pass

            if ext_out == "png":
                cairosvg.svg2png(url=str(in_p), write_to=str(out_p), **kwargs)
            elif ext_out in ["jpg", "jpeg"]:
                temp_png = out_p.with_suffix(".temp.png")
                cairosvg.svg2png(url=str(in_p), write_to=str(temp_png), **kwargs)
                with Image.open(temp_png) as img:
                    rgb_img = img.convert("RGB")
                    rgb_img.save(str(out_p), quality=quality)
                if temp_png.exists():
                    os.remove(temp_png)
            elif ext_out == "pdf":
                cairosvg.svg2pdf(url=str(in_p), write_to=str(out_p), **kwargs)
            
            if progress_callback:
                progress_callback(100.0, 0.0, "00:00")
            return True

        # Cas 2: Image source photographique RAW
        if ext_in in cls.RAW_EXTENSIONS and RAWPY_AVAILABLE:
            with rawpy.imread(str(in_p)) as raw:
                rgb = raw.postprocess()
                img = Image.fromarray(rgb)
        else:
            # Cas 3: Raster standard via Pillow (gère PNG, JPG, WebP, AVIF, HEIC, TIFF, BMP, TGA, PSD, ICO...)
            img = Image.open(str(in_p))

        # Redimensionnement vers très haute résolution (ex: 4K, 8K, 12K)
        if resolution and "x" in resolution:
            try:
                rw, rh = resolution.lower().split("x")
                target_w, target_h = int(rw), int(rh)
                img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
            except Exception:
                pass

        if progress_callback:
            progress_callback(50.0, 0.0, "--:--")

        # Normalisation des canaux de couleur selon format de sortie
        if ext_out in ["jpg", "jpeg", "bmp"]:
            if img.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                background.paste(img, mask=img.split()[-1])
                img = background
            elif img.mode != "RGB":
                img = img.convert("RGB")
        elif ext_out in ["png", "webp", "avif", "tiff", "tga"]:
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGBA")

        # Enregistrement avec paramètres optimisés
        save_kwargs = {}
        if ext_out in ["jpg", "jpeg", "webp"]:
            save_kwargs["quality"] = quality
            if ext_out == "webp":
                save_kwargs["method"] = 2  # Accélération pour les très grandes images 8K/12K
                if quality >= 100:
                    save_kwargs["lossless"] = True
        elif ext_out == "png":
            save_kwargs["optimize"] = True
        elif ext_out == "tiff":
            save_kwargs["compression"] = "tiff_lzw"
        elif ext_out == "ico":
            img = img.resize((256, 256), Image.Resampling.LANCZOS)

        # Sauvegarde
        try:
            img.save(str(out_p), **save_kwargs)
        except Exception:
            # Fallback direct sans save_kwargs si le format a des exigences strictes
            img.convert("RGB").save(str(out_p))

        if progress_callback:
            progress_callback(100.0, 0.0, "00:00")

        return True

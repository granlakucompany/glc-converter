"""
GLC CONVERTER — Politique des encodeurs vidéo haute performance
Éditeur: GRAN LAKU COMPANY | https://granlaku.com/glcconverter

GLC CONVERTER est distribué gratuitement et en Open Source sur GitHub.
Tous les encodeurs de référence haute performance sont pleinement autorisés et intégrés :
  - Accélération matérielle GPU : NVIDIA NVENC, Intel QSV, AMD AMF, Windows Media Foundation (MFT) ;
  - Encodeurs de référence mondiaux : libx264 (H.264), libx265 (HEVC), libopenh264 ;
  - Encodeurs nouvelle génération & broadcast : SVT-AV1, libvpx-vp9, Apple ProRes (prores_ks).

Chaque candidat est réellement ouvert à la résolution demandée avant d'être retenu :
les limites matérielles des cartes graphiques (ex. GPU H.264 limité à 4096 px)
basculent automatiquement vers HEVC/AV1 matériels ou les encodeurs logiciels ultra-optimisés.
"""
from fractions import Fraction
from typing import Dict, List, Optional, Tuple

import av
from av.codec.codec import Codec

# Encodeurs restreints ou non redistribuables (ex. formats propriétaires fermés non libres)
FORBIDDEN_ENCODERS = frozenset({
    "libfdk_aac",
})

_HW_ENCODERS = {
    "h264": ["h264_nvenc", "h264_qsv", "h264_amf", "h264_mf"],
    "hevc": ["hevc_nvenc", "hevc_qsv", "hevc_amf", "hevc_mf"],
    "av1": ["av1_nvenc", "av1_qsv", "av1_amf", "av1_mf"],
}

_FAMILY_ALIASES = {
    "h264": "h264", "avc": "h264",
    "h265": "hevc", "hevc": "hevc",
    "av1": "av1", "vp9": "vp9",
    "prores": "prores", "prores_ks": "prores",
    "mpeg4": "mpeg4",
}

# Familles de codecs vérifiées dans chaque conteneur (AV1 refusé par le muxeur .mov).
_CONTAINER_FAMILIES = {
    "mp4": {"h264", "hevc", "av1", "vp9", "mpeg4"},
    "m4v": {"h264", "hevc", "av1", "vp9", "mpeg4"},
    "mov": {"h264", "hevc", "prores", "mpeg4"},
    "mkv": {"h264", "hevc", "av1", "vp9", "prores", "mpeg4"},
    "webm": {"vp9", "av1"},
    "avi": {"h264", "mpeg4"},
    "ts": {"h264", "hevc", "mpeg2"},
    "m2ts": {"h264", "hevc", "mpeg2"},
    "mxf": {"mpeg2"},
    "flv": {"h264", "flv"},
    "wmv": {"wmv"},
}

# Replis logiciels haute performance par conteneur, après le matériel.
_SOFTWARE_FALLBACK = {
    "mp4": ["libx264", "libopenh264", "libsvtav1", "mpeg4"],
    "m4v": ["libx264", "libopenh264", "libsvtav1", "mpeg4"],
    "mov": ["libx264", "prores_ks", "mpeg4"],
    "mkv": ["libx264", "libx265", "libsvtav1", "libvpx-vp9", "mpeg4"],
    "webm": ["libvpx-vp9", "libsvtav1"],
    "avi": ["libx264", "mpeg4"],
    "ts": ["libx264", "libx265", "mpeg2video"],
    "m2ts": ["libx264", "libx265", "mpeg2video"],
    "mxf": ["mpeg2video"],
    "flv": ["libx264", "flv"],
    "wmv": ["wmv2"],
}

_open_cache: Dict[Tuple[str, int, int, str], bool] = {}


def is_allowed(encoder_name: str) -> bool:
    """Vrai si l'encodeur est autorisé dans GLC CONVERTER."""
    return encoder_name.lower() not in FORBIDDEN_ENCODERS


def encoder_family(encoder_name: str) -> str:
    """Famille de codec produite par un encodeur (h264, hevc, av1, vp9, prores…)."""
    name = encoder_name.lower()
    if name.startswith("h264") or name in ("libopenh264", "libx264", "libx264rgb"):
        return "h264"
    if name.startswith("hevc") or name in ("libkvazaar", "libx265"):
        return "hevc"
    if name.startswith("av1") or name in ("libsvtav1", "libaom-av1", "librav1e"):
        return "av1"
    if "vpx-vp9" in name or name == "vp9":
        return "vp9"
    if name.startswith("prores"):
        return "prores"
    if name.startswith("mpeg2"):
        return "mpeg2"
    if name.startswith("wmv"):
        return "wmv"
    return _FAMILY_ALIASES.get(name, name)


def video_encoder_chain(codec: str, container: str, allow_hw: bool = True) -> List[str]:
    """Chaîne ordonnée d'encodeurs autorisés pour un codec et un conteneur, sans test d'ouverture."""
    family = _FAMILY_ALIASES.get((codec or "h264").lower(), "h264")
    ext = (container or "mp4").lower().lstrip(".")
    allowed_families = _CONTAINER_FAMILIES.get(ext, {"h264", "hevc", "av1", "vp9", "mpeg4"})

    chain: List[str] = []
    if ext == "webm":
        family = "av1" if family == "av1" else "vp9"
    if family == "prores":
        chain += ["prores_ks", "prores"]
    elif family == "vp9":
        chain += ["libvpx-vp9"]
    elif family == "mpeg4":
        chain += ["mpeg4"]
    else:
        if allow_hw:
            # Un H.264 trop grand pour la carte graphique bascule sur HEVC puis AV1 matériels.
            for fam in {"h264": ["h264", "hevc", "av1"], "hevc": ["hevc", "av1"], "av1": ["av1"]}[family]:
                chain += _HW_ENCODERS[fam]
        if family == "h264":
            chain.append("libx264")
            chain.append("libx264rgb")
            chain.append("libopenh264")
        elif family == "hevc":
            chain.append("libx265")
            chain.append("libkvazaar")  # HEVC logiciel
        chain.append("libsvtav1")
    chain += _SOFTWARE_FALLBACK.get(ext, ["mpeg4"])

    result: List[str] = []
    for name in chain:
        if name in result or not is_allowed(name):
            continue
        if encoder_family(name) not in allowed_families:
            continue
        if name not in av.codec.codecs_available:
            continue
        result.append(name)
    return result


def pixel_format_for(encoder_name: str) -> str:
    """Format de pixel accepté par l'encodeur (yuv420p de préférence, nv12 pour QuickSync/MFT)."""
    if encoder_name.lower().startswith("prores"):
        return "yuv422p10le"
    try:
        formats = [f.name for f in (Codec(encoder_name, "w").video_formats or [])]
    except Exception:
        return "yuv420p"
    for preferred in ("yuv420p", "nv12"):
        if preferred in formats:
            return preferred
    return formats[0] if formats else "yuv420p"


def can_open(encoder_name: str, width: int, height: int, pix_fmt: Optional[str] = None) -> bool:
    """Ouvre réellement l'encodeur à cette résolution (détecte GPU absent ou taille hors limite)."""
    pix_fmt = pix_fmt or pixel_format_for(encoder_name)
    key = (encoder_name, int(width), int(height), pix_fmt)
    if key not in _open_cache:
        try:
            ctx = av.CodecContext.create(encoder_name, "w")
            ctx.width = int(width)
            ctx.height = int(height)
            ctx.pix_fmt = pix_fmt
            ctx.time_base = Fraction(1, 30)
            ctx.open()
            _open_cache[key] = True
        except Exception:
            _open_cache[key] = False
    return _open_cache[key]


def usable_video_encoders(
    codec: str, container: str, width: int, height: int, allow_hw: bool = True
) -> List[Tuple[str, str]]:
    """Encodeurs autorisés qui s'ouvrent réellement à cette résolution : [(encodeur, pix_fmt), …]."""
    usable = []
    for name in video_encoder_chain(codec, container, allow_hw):
        pix_fmt = pixel_format_for(name)
        if can_open(name, width, height, pix_fmt):
            usable.append((name, pix_fmt))
    return usable


def pick_video_encoder(
    codec: str, container: str, width: int, height: int, allow_hw: bool = True
) -> Tuple[str, str]:
    """Premier encodeur autorisé et utilisable ; lève RuntimeError si aucun ne convient."""
    usable = usable_video_encoders(codec, container, width, height, allow_hw)
    if not usable:
        raise RuntimeError(
            f"Aucun encodeur vidéo disponible pour {codec} en .{container.lstrip('.')} à {width}x{height}."
        )
    return usable[0]


def encoder_options(encoder_name: str, width: int, height: int, crf: int, target_bitrate: int) -> Tuple[Dict[str, str], Optional[int]]:
    """Options de qualité adaptées à l'encodeur : (options, débit vidéo ou None)."""
    enc = encoder_name.lower()
    if "nvenc" in enc:
        bitrate = int(target_bitrate * 0.75) if not enc.startswith("h264") else target_bitrate
        return {
            "preset": "p5", "tune": "hq", "rc": "vbr", "cq": str(min(18, crf)),
            "b:v": str(bitrate), "maxrate": str(int(bitrate * 1.3)), "bufsize": str(int(bitrate * 2)),
        }, bitrate
    if "qsv" in enc:
        return {
            "global_quality": str(min(20, crf)),
            "b:v": str(target_bitrate), "maxrate": str(int(target_bitrate * 1.3)),
        }, target_bitrate
    if "amf" in enc:
        return {
            "rc": "cqp", "qp_i": str(min(18, crf)), "qp_p": str(min(18, crf)), "b:v": str(target_bitrate),
        }, target_bitrate
    if "mf" in enc:
        # Windows Media Foundation (MFT natif matériel / optimisé)
        return {"b:v": str(target_bitrate)}, target_bitrate
    if enc in ("libx264", "libx264rgb"):
        preset = "veryfast" if (width >= 3840 or height >= 2160) else "medium"
        return {"preset": preset, "crf": str(crf)}, target_bitrate
    if enc == "libx265":
        preset = "fast" if (width >= 3840 or height >= 2160) else "medium"
        return {"preset": preset, "crf": str(min(28, crf + 4))}, int(target_bitrate * 0.75)
    if enc == "libopenh264":
        return {"rc_mode": "bitrate", "allow_skip_frames": "0"}, target_bitrate
    if enc == "libkvazaar":
        return {"kvazaar-params": "preset=veryfast"}, int(target_bitrate * 0.75)
    if enc == "libsvtav1":
        preset = "10" if (width >= 7680 or height >= 4320) else "8"
        return {"crf": str(max(20, min(40, crf + 12))), "preset": preset}, None
    if "vpx" in enc:
        return {"crf": str(min(18, crf)), "b:v": str(target_bitrate), "deadline": "good", "cpu-used": "2"}, target_bitrate
    if enc.startswith("prores"):
        return {"profile": "3"}, int(target_bitrate * 2.5)  # ProRes 422 HQ
    if enc in ("mpeg4", "mpeg2video", "flv", "wmv2"):
        return {"maxrate": str(int(target_bitrate * 1.3)), "bufsize": str(int(target_bitrate * 2))}, target_bitrate
    return {}, target_bitrate


def default_bitrate(width: int, height: int) -> int:
    """Débit cible haute fidélité selon la résolution."""
    if width >= 11520 or height >= 6480:
        return 160_000_000
    if width >= 7680 or height >= 4320:
        return 95_000_000
    if width >= 3840 or height >= 2160:
        return 45_000_000
    if width >= 1920 or height >= 1080:
        return 18_000_000
    if width <= 1280 and height <= 720:
        return 8_000_000
    return 12_000_000


def add_video_stream(container, codec: str, out_ext: str, width: int, height: int, fps, crf: int = 18, allow_hw: bool = True):
    """Ajoute au conteneur un flux vidéo encodé sans GPL ; retourne (flux, encodeur, pix_fmt)."""
    encoder, pix_fmt = pick_video_encoder(codec, out_ext, width, height, allow_hw)
    stream = container.add_stream(encoder, rate=fps)
    stream.width = width
    stream.height = height
    stream.pix_fmt = pix_fmt
    opts, bitrate = encoder_options(encoder, width, height, crf, default_bitrate(width, height))
    if opts:
        stream.options = opts
    if bitrate:
        stream.bit_rate = bitrate
    return stream, encoder, pix_fmt

"""
GLC CONVERTER — Détecteur Intelligent de Métadonnées HTML, Animations & Audio
Éditeur: GRAN LAKU COMPANY | https://granlaku.com/glcconverter

Analyse les composants HTML / Canvas / WebGL / Kadans / Remotion pour extraire :
- Durée exacte totale (évite toute coupure prématurée)
- Résolution native (1080x1920 portrait, 1920x1080 landscape, 4K, 8K)
- Cadence d'images (FPS)
- Piste audio (voix, musique, ambiance) pour synchronisation complète
"""
import re
import json
from pathlib import Path
from typing import Dict, Any, Optional

import av


class HtmlDetector:
    """Détecte les métadonnées vidéo et audio d'une animation ou page HTML."""

    @classmethod
    def detect_html_metadata(cls, html_path: str) -> Dict[str, Any]:
        """
        Extrait la durée réelle, les dimensions, le framerate et la piste audio associée.
        """
        path = Path(html_path)
        result: Dict[str, Any] = {
            "duration": 5.0,
            "width": 1920,
            "height": 1080,
            "fps": 30,
            "audio_path": None,
            "title": path.stem,
            "has_audio": False
        }

        content = ""
        parent_dir = path.parent
        s_raw = str(html_path).strip()
        is_http = s_raw.startswith(("http://", "https://"))

        if is_http:
            import urllib.request
            from urllib.parse import urlparse, unquote
            parsed = urlparse(s_raw)
            # 1. Si localhost / 127.0.0.1 sous XAMPP (Windows), mapper directement sur C:/xampp/htdocs
            if parsed.hostname in ("localhost", "127.0.0.1"):
                rel_url = unquote(parsed.path).lstrip("/")
                xampp_cand = Path(r"C:\xampp\htdocs") / rel_url
                if xampp_cand.exists():
                    path = xampp_cand
                    parent_dir = path.parent
                    result["title"] = path.stem
                    try:
                        content = path.read_text(encoding="utf-8", errors="ignore")
                    except Exception:
                        content = ""
            # 2. Si pas trouvé en local XAMPP, télécharger via urllib
            if not content:
                try:
                    req = urllib.request.Request(s_raw, headers={"User-Agent": "GLC-Converter/1.0"})
                    with urllib.request.urlopen(req, timeout=3.0) as resp:
                        content = resp.read().decode("utf-8", errors="ignore")
                except Exception:
                    pass
        elif path.exists():
            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                return result
        else:
            return result

        # ----------------------------------------------------------------------
        # 1. Détection des Dimensions (Largeur & Hauteur)
        # ----------------------------------------------------------------------
        w_found = None
        h_found = None

        # A) data-width / data-height sur #stage ou autre balise
        m_w = re.search(r'data-width=["\']?(\d+)["\']?', content)
        m_h = re.search(r'data-height=["\']?(\d+)["\']?', content)
        if m_w and m_h:
            w_found = int(m_w.group(1))
            h_found = int(m_h.group(1))

        # B) window.__kadans = { ... "w": 1080, "h": 1920 ... }
        if not w_found:
            m_kad = re.search(r'window\.__kadans\s*=\s*(\{.*?\});', content, re.DOTALL)
            if m_kad:
                try:
                    k_data = json.loads(m_kad.group(1))
                    if "w" in k_data and "h" in k_data:
                        w_found = int(k_data["w"])
                        h_found = int(k_data["h"])
                    if "fps" in k_data:
                        result["fps"] = int(k_data["fps"])
                    if "total" in k_data:
                        result["duration"] = float(k_data["total"])
                except Exception:
                    pass

        # C) CSS #stage { width: ...; height: ... }
        if not w_found:
            m_stage = re.search(r'#stage\s*\{[^}]*?width:\s*(\d+)px;[^}]*?height:\s*(\d+)px', content, re.IGNORECASE)
            if m_stage:
                w_found = int(m_stage.group(1))
                h_found = int(m_stage.group(2))

        # D) Détection portrait / vertical
        if not w_found:
            if 'class="portrait"' in content or "portrait" in content:
                w_found = 1080
                h_found = 1920

        # E) Détection XML / SVG (balises width/height ou viewBox)
        if not w_found:
            m_svg = re.search(r'<svg[^>]*?width=["\']?(\d+)px?["\']?[^>]*?height=["\']?(\d+)px?["\']?', content, re.IGNORECASE)
            if m_svg:
                w_found = int(m_svg.group(1))
                h_found = int(m_svg.group(2))
            else:
                m_vb = re.search(r'viewBox=["\']\s*[\d.]+\s+[\d.]+\s+([\d.]+)\s+([\d.]+)\s*["\']', content, re.IGNORECASE)
                if m_vb:
                    try:
                        w_found = int(float(m_vb.group(1)))
                        h_found = int(float(m_vb.group(2)))
                    except Exception:
                        pass

        if w_found and h_found:
            result["width"] = w_found
            result["height"] = h_found

        # ----------------------------------------------------------------------
        # 2. Détection du Framerate (FPS)
        # ----------------------------------------------------------------------
        m_fps = re.search(r'data-fps=["\']?(\d+)["\']?', content)
        if m_fps:
            result["fps"] = int(m_fps.group(1))

        # ----------------------------------------------------------------------
        # 3. Détection de la Durée Réelle (Durée complète sans coupure)
        # ----------------------------------------------------------------------
        dur_found = None

        # A) data-duration sur #stage
        m_dur = re.search(r'data-duration=["\']?([\d.]+)["\']?', content)
        if m_dur:
            try:
                dur_found = float(m_dur.group(1))
            except Exception:
                pass

        # B) Détection XML / SMIL / SVG animations (dur="5s", duration="10s")
        m_durs = re.findall(r'(?:dur|duration)=["\']?([\d.]+)(ms|s)?["\']?', content, re.IGNORECASE)
        if m_durs:
            max_svg_dur = 0.0
            for val_str, unit in m_durs:
                try:
                    val = float(val_str)
                    if unit and unit.lower() == "ms":
                        val /= 1000.0
                    if val > max_svg_dur:
                        max_svg_dur = val
                except Exception:
                    pass
            if max_svg_dur > 0:
                dur_found = max(dur_found or 0.0, max_svg_dur)

        # B) Somme ou fin de scènes <section class="scene" data-start="X" data-duration="Y">
        scene_matches = re.findall(r'data-start=["\']?([\d.]+)["\']?[^>]*?data-duration=["\']?([\d.]+)["\']?', content)
        if scene_matches:
            max_end = 0.0
            for st_str, d_str in scene_matches:
                try:
                    end_val = float(st_str) + float(d_str)
                    if end_val > max_end:
                        max_end = end_val
                except Exception:
                    pass
            if max_end > 0:
                dur_found = max(dur_found or 0.0, max_end)

        # C) Recherche spec.json dans le même dossier
        spec_path = parent_dir / "spec.json"
        if spec_path.exists():
            try:
                spec_data = json.loads(spec_path.read_text(encoding="utf-8", errors="ignore"))
                if "total" in spec_data:
                    dur_found = max(dur_found or 0.0, float(spec_data["total"]))
                elif "duration" in spec_data:
                    dur_found = max(dur_found or 0.0, float(spec_data["duration"]))
            except Exception:
                pass

        # ----------------------------------------------------------------------
        # 4. Détection et Localisation de la Piste Audio & Voix
        # ----------------------------------------------------------------------
        audio_candidate = None

        # A) Fichiers audio pré-rendus maîtres dans le dossier du composant
        priority_audio_names = [
            "preview-audio.raw.wav",
            "preview-audio.wav",
            "preview-sounds.m4a",
            "audio.wav",
            "audio.mp3",
            "voice.wav",
            "sound.wav",
            "master_audio.wav",
            "output.wav"
        ]

        if parent_dir.exists():
            for aname in priority_audio_names:
                c_path = parent_dir / aname
                if c_path.exists() and c_path.stat().st_size > 1024:
                    audio_candidate = str(c_path.resolve())
                    break

        # B) Balises <audio src="..."> ou <source src="..."> dans le HTML
        if not audio_candidate:
            audio_tag_matches = re.findall(r'<audio[^>]*?src=["\']([^"\']+)["\']', content, re.IGNORECASE)
            if not audio_tag_matches:
                audio_tag_matches = re.findall(r'<source[^>]*?src=["\']([^"\']+\.(?:wav|mp3|m4a|aac|ogg|flac))["\']', content, re.IGNORECASE)
            
            for rel_src in audio_tag_matches:
                # Éviter les URLs distantes http://
                if rel_src.startswith("http://") or rel_src.startswith("https://"):
                    continue
                a_file = (parent_dir / rel_src).resolve()
                if a_file.exists() and a_file.stat().st_size > 1024:
                    audio_candidate = str(a_file)
                    break

        # C) Recherche dans audio_map.json
        audio_map_path = parent_dir / "audio_map.json"
        if not audio_candidate and audio_map_path.exists():
            try:
                amap = json.loads(audio_map_path.read_text(encoding="utf-8", errors="ignore"))
                # Si un mix est défini
                if amap.get("mix"):
                    mix_file = (parent_dir / amap["mix"]).resolve()
                    if mix_file.exists():
                        audio_candidate = str(mix_file)
                # Sinon si musique définie
                if not audio_candidate and amap.get("music"):
                    mus_file = (parent_dir / amap["music"]).resolve()
                    if mus_file.exists():
                        audio_candidate = str(mus_file)
            except Exception:
                pass

        # D) Sous-dossiers medya/vwa ou medya/mizik
        if not audio_candidate:
            vwa_dir = parent_dir / "medya" / "vwa"
            if vwa_dir.exists():
                wavs = list(vwa_dir.glob("*.wav"))
                if wavs:
                    # S'il y a un seul fichier voix ou un premier
                    audio_candidate = str(wavs[0].resolve())

        # Si un fichier audio a été trouvé, vérifier sa durée réelle via PyAV
        if audio_candidate and Path(audio_candidate).exists():
            result["audio_path"] = audio_candidate
            result["has_audio"] = True
            try:
                with av.open(audio_candidate) as container:
                    if container.streams.audio:
                        a_dur = float(container.duration) / 1e6 if container.duration else None
                        if a_dur and a_dur > 0.5:
                            # La durée audio est la durée idéale si plus précise
                            dur_found = max(dur_found or 0.0, a_dur)
            except Exception:
                pass

        if dur_found and dur_found > 0:
            result["duration"] = round(dur_found, 2)
        else:
            result["duration"] = 5.0

        return result

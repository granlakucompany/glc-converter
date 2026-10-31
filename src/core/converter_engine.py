"""
GLC CONVERTER — Moteur Central Unifié & Orchestrateur Multi-Formats
Éditeur: GRAN LAKU COMPANY | https://granlaku.com/glcconverter
"""
import os
import re
import secrets
import threading
from pathlib import Path
from typing import Dict, Any, Callable, Optional, List, Set, Tuple
from .mime_detector import MimeDetector
from .video_engine import VideoEngine
from .audio_engine import AudioEngine
from .image_engine import ImageEngine
from .doc_engine import DocEngine
from .html_video_engine import HtmlVideoEngine
from .model3d_engine import Model3DEngine
from .graph_router import GraphRouter

# Registre global thread-safe des chemins alloués pour éviter les collisions en mémoire et sur disque
_allocated_output_paths: Set[str] = set()
_allocated_lock = threading.Lock()

def clean_base_stem(input_path_or_stem: str) -> str:
    """
    Nettoie le nom de base d'un fichier ou d'une URL en retirant les résidus répétitifs
    tels que '_glc', '_GLC', '_GLC_A1B2C3D4' pour éviter l'accumulation
    chaotique de suffixes comme 'fichier_glc_glc.mp4'.
    """
    s = str(input_path_or_stem).strip()
    if s.startswith("http://") or s.startswith("https://"):
        from urllib.parse import urlparse
        p_url = urlparse(s)
        slug = (p_url.path.strip("/").replace("/", "_") or p_url.netloc.replace(":", "_").replace(".", "_"))
        slug = re.sub(r'[^a-zA-Z0-9_-]', '_', slug).strip("_")
        return slug or "web_capture"

    raw_name = Path(input_path_or_stem).name
    if raw_name.startswith(".") and raw_name.count(".") == 1:
        return "media"

    p = Path(input_path_or_stem)
    stem = p.stem.lstrip(".")
    prev = None
    while prev != stem:
        prev = stem
        stem = re.sub(r'(_GLC(_[0-9A-Za-z]+)?)$', '', stem, flags=re.IGNORECASE)
        stem = re.sub(r'(_glc)$', '', stem, flags=re.IGNORECASE)
        stem = stem.strip(" _-")
    if not stem:
        stem = "media"
    return stem

def generate_unique_glc_output_path(
    output_dir: str,
    input_path: str,
    output_format: str,
    preferred_code: Optional[str] = None
) -> Tuple[str, str]:
    """
    Génère un chemin de sortie unique avec signature officielle GLC et code d'identification unique.
    Garantit qu'aucun fichier ne sera écrasé même s'ils vont dans le même dossier
    et qu'aucune collision de code ne se produit.
    
    Format : {clean_base}_GLC_{UNIQUE_CODE}.{format}
    Exemple : composition_GLC_A7F9B2C4.mp4
    
    Retourne : (output_path_unique, unique_code)
    """
    clean_base = clean_base_stem(input_path)
    out_dir_path = Path(output_dir)
    out_dir_path.mkdir(parents=True, exist_ok=True)
    fmt = output_format.lower().lstrip(".")
    
    # Code d'identification unique : 8 caractères hexadécimaux majuscules (ex: 'A7F9B2C4')
    # Plus de 4.3 milliards de combinaisons possibles
    code = preferred_code.upper() if preferred_code else secrets.token_hex(4).upper()
    
    with _allocated_lock:
        while True:
            filename = f"{clean_base}_GLC_{code}.{fmt}"
            candidate_path = str(out_dir_path / filename)
            
            # Vérifier si le fichier existe physiquement sur le disque
            # OU s'il est déjà réservé en mémoire par une autre tâche
            is_collision = Path(candidate_path).exists() or (candidate_path in _allocated_output_paths)
            
            if not is_collision:
                _allocated_output_paths.add(candidate_path)
                return candidate_path, code
            
            # En cas de collision (fichier déjà existant sur disque ou code déjà pris),
            # générer immédiatement un nouveau code cryptographiquement unique
            code = secrets.token_hex(4).upper()

def clear_allocated_output_paths():
    """Vide le registre global des chemins réservés en mémoire."""
    with _allocated_lock:
        _allocated_output_paths.clear()

class ConversionTask:
    """Représente une tâche de conversion individuelle dans la file d'attente."""
    def __init__(
        self,
        task_id: str,
        input_path: str,
        output_format: str,
        output_dir: str,
        options: Optional[Dict[str, Any]] = None,
        file_info: Optional[Dict[str, Any]] = None,
        output_path: Optional[str] = None
    ):
        self.task_id = task_id or secrets.token_hex(4).upper()
        self.input_path = input_path
        self.output_format = output_format.lower().lstrip(".")
        self.output_dir = output_dir
        self.options = options or {}
        
        self.file_info = file_info if file_info is not None else MimeDetector.identify_file(input_path)

        # Attribution sécurisée du chemin de sortie anti-collision et code unique GLC
        if output_path is not None:
            p = Path(output_path)
            with _allocated_lock:
                already_taken = p.exists() or (str(p) in _allocated_output_paths)
            if already_taken:
                self.output_path, self.unique_code = generate_unique_glc_output_path(
                    output_dir=str(p.parent),
                    input_path=p.stem,
                    output_format=p.suffix.lstrip(".") or self.output_format
                )
            else:
                self.output_path = str(p)
                with _allocated_lock:
                    _allocated_output_paths.add(self.output_path)
                self.unique_code = self.task_id[:8].upper()
        else:
            self.output_path, self.unique_code = generate_unique_glc_output_path(
                output_dir=self.output_dir,
                input_path=self.input_path,
                output_format=self.output_format,
                preferred_code=self.task_id[:8].upper()
            )
        
        self.status = "En attente" # "En cours", "Terminé", "Erreur", "Annulé"
        self.progress = 0.0
        self.speed = 0.0
        self.eta = "--:--"
        self.error_message = ""
        self.is_cancelled = False

    def release(self):
        """Libère la réservation du chemin de sortie pour permettre une réallocation propre si retiré."""
        with _allocated_lock:
            _allocated_output_paths.discard(self.output_path)

    def cancel(self):
        self.is_cancelled = True
        self.status = "Annulé"
        self.release()


class ConverterEngine:
    """Orchestrateur global des conversions de GLC CONVERTER."""

    def __init__(self):
        self.router = GraphRouter()
        self.active_tasks: List[ConversionTask] = []
        self._lock = threading.Lock()

    def process_task(
        self,
        task: ConversionTask,
        on_progress: Optional[Callable[[ConversionTask], None]] = None,
        on_finish: Optional[Callable[[ConversionTask], None]] = None
    ):
        """Exécute une tâche de conversion de manière synchrone (à appeler dans un thread worker)."""
        task.status = "En cours"
        if on_progress:
            on_progress(task)

        src_ext = task.file_info.get("extension", "").lower()
        dst_ext = task.output_format.lower()
        src_cat = task.file_info.get("category", "")

        def progress_cb(pct: float, spd: float, eta_str: str):
            task.progress = pct
            task.speed = spd
            task.eta = eta_str
            if on_progress:
                on_progress(task)

        def cancel_check() -> bool:
            return task.is_cancelled

        try:
            success = False

            # 1. Conversion Web / HTML / XML / Animations / Lottie vers Vidéo
            if src_cat == "web" or src_ext in ["html", "htm", "xml", "xhtml", "json"]:
                if dst_ext in ["mp4", "mov", "webm", "mkv"]:
                    detected = {}
                    if src_ext in ["html", "htm", "xml", "xhtml"]:
                        try:
                            from .html_detector import HtmlDetector
                            detected = HtmlDetector.detect_html_metadata(task.input_path)
                        except Exception:
                            detected = {}

                    duration = float(task.options.get("duration") or detected.get("duration") or 5.0)
                    fps = int(task.options.get("fps") or detected.get("fps") or 30)

                    # Résolution cible (priorité au choix explicite de l'utilisateur, ex: 4K, 8K, 1080p)
                    res_opt = task.options.get("resolution")
                    target_w, target_h = None, None
                    if res_opt and "x" in res_opt:
                        try:
                            rw, rh = res_opt.lower().split("x")
                            target_w = int(rw)
                            target_h = int(rh)
                        except Exception:
                            pass

                    width = target_w or int(task.options.get("width") or detected.get("width") or 1920)
                    height = target_h or int(task.options.get("height") or detected.get("height") or 1080)
                    crf = int(task.options.get("crf", 16))
                    audio_path = task.options.get("audio_path") or detected.get("audio_path")

                    success = HtmlVideoEngine.convert_html_to_video(
                        task.input_path,
                        task.output_path,
                        duration_sec=duration,
                        fps=fps,
                        width=width,
                        height=height,
                        crf=crf,
                        audio_path=audio_path,
                        progress_callback=progress_cb,
                        cancel_check=cancel_check
                    )
                else:
                    raise ValueError(f"Les animations Web doivent être converties en Vidéo (MP4/WebM/MOV).")

            # 2. Modèles 3D vers Vidéo 360° ou formats 3D
            elif src_cat == "3d" or src_ext in ["obj", "stl", "gltf", "glb", "ply", "fbx"]:
                success = Model3DEngine.convert_3d(
                    input_path=task.input_path,
                    output_path=task.output_path,
                    resolution=task.options.get("resolution", "1920x1080"),
                    duration_sec=float(task.options.get("duration", 6.0)),
                    fps=int(task.options.get("fps", 30)),
                    progress_callback=progress_cb,
                    cancel_check=cancel_check
                )

            # 3. Image vers Vidéo (ex: PNG -> MP4 / MOV / WebM)
            elif (src_cat == "image" or src_ext in ["png", "jpg", "jpeg", "webp", "svg", "bmp", "tiff"]) and dst_ext in [
                "mp4", "mov", "webm", "mkv", "avi"
            ]:
                success = VideoEngine.image_to_video(
                    image_path=task.input_path,
                    output_path=task.output_path,
                    duration_sec=float(task.options.get("duration", 5.0)),
                    fps=int(task.options.get("fps", 30)),
                    resolution=task.options.get("resolution"),
                    progress_callback=progress_cb,
                    cancel_check=cancel_check
                )

            # 4. Vidéo vers Image (Extraction poster / keyframe)
            elif src_cat == "video" and dst_ext in ["png", "jpg", "jpeg", "webp", "bmp", "tiff"]:
                success = VideoEngine.video_to_image(
                    video_path=task.input_path,
                    output_path=task.output_path,
                    progress_callback=progress_cb
                )

            # 5. Vidéo vers Audio (Extraction de piste sonore)
            elif src_cat == "video" and dst_ext in [
                "mp3", "wav", "flac", "aac", "ogg", "opus", "m4a", "aiff", "alac", "ac3", "wma"
            ]:
                success = AudioEngine.convert_audio(
                    input_path=task.input_path,
                    output_path=task.output_path,
                    target_format=dst_ext,
                    bitrate=task.options.get("bitrate", "320k"),
                    sample_rate=task.options.get("sample_rate", 44100),
                    progress_callback=progress_cb,
                    cancel_check=cancel_check
                )

            # 6. Vidéo vers Vidéo (Transcodage Ultra-HD jusqu'au 12K)
            elif src_cat == "video" and dst_ext in [
                "mp4", "mkv", "mov", "webm", "avi", "flv", "wmv", "ts", "m2ts", "mxf", "prores"
            ]:
                success = VideoEngine.convert_video(
                    input_path=task.input_path,
                    output_path=task.output_path,
                    target_codec=task.options.get("video_codec", "h264"),
                    crf=task.options.get("crf", 22),
                    bitrate=task.options.get("bitrate"),
                    resolution=task.options.get("resolution"),
                    fps=task.options.get("fps"),
                    hw_accel=task.options.get("hw_accel", True),
                    progress_callback=progress_cb,
                    cancel_check=cancel_check
                )

            # 7. Audio vers Audio (Hi-Fi, Lossless, Multi-Canal)
            elif src_cat == "audio" and dst_ext in [
                "mp3", "wav", "flac", "aac", "ogg", "opus", "m4a", "aiff", "alac", "ac3", "wma"
            ]:
                success = AudioEngine.convert_audio(
                    input_path=task.input_path,
                    output_path=task.output_path,
                    target_format=dst_ext,
                    bitrate=task.options.get("bitrate", "320k"),
                    sample_rate=task.options.get("sample_rate", 44100),
                    progress_callback=progress_cb,
                    cancel_check=cancel_check
                )

            # 8. Conversion Image (Raster, Vectoriel, RAW jusqu'au 12K)
            elif (src_cat == "image" or src_ext in [
                "png", "jpg", "jpeg", "webp", "avif", "heic", "tiff", "bmp", "tga", "qoi", "jxl",
                "psd", "psb", "exr", "hdr", "svg", "eps", "ai", "dng", "cr2", "nef", "arw", "ico"
            ]) and dst_ext in [
                "png", "jpg", "jpeg", "webp", "avif", "heic", "tiff", "bmp", "tga", "ico", "pdf"
            ]:
                success = ImageEngine.convert_image(
                    input_path=task.input_path,
                    output_path=task.output_path,
                    quality=task.options.get("quality", 90),
                    resolution=task.options.get("resolution"),
                    progress_callback=progress_cb
                )

            # 9. Conversion Documents (PDF, DOCX, TXT, MD, etc.)
            elif src_cat == "document" or src_ext in ["pdf", "docx", "pptx", "xlsx", "txt", "md", "rtf"]:
                success = DocEngine.convert_document(
                    input_path=task.input_path,
                    output_path=task.output_path,
                    progress_callback=progress_cb
                )

            else:
                # Routage par graphe universel si aucun convertisseur direct
                path = self.router.find_shortest_path(src_ext, dst_ext)
                if path:
                    # Exécuter les étapes pivots
                    curr_in = task.input_path
                    for step_idx, (p_src, p_dst, p_method) in enumerate(path):
                        is_last = (step_idx == len(path) - 1)
                        step_out = task.output_path if is_last else f"{task.output_path}.step_{step_idx}.{p_dst}"
                        
                        subtask = ConversionTask(
                            task_id=f"{task.task_id}_s{step_idx}",
                            input_path=curr_in,
                            output_format=p_dst,
                            output_dir=task.output_dir,
                            options=task.options,
                            output_path=step_out
                        )
                        self.process_task(subtask)
                        
                        if subtask.status != "Terminé":
                            raise RuntimeError(f"Échec étape pivot {p_src} -> {p_dst}: {subtask.error_message}")
                        
                        if curr_in != task.input_path and Path(curr_in).exists():
                            try:
                                os.remove(curr_in)
                            except Exception:
                                pass
                        curr_in = step_out
                    success = True
                else:
                    raise NotImplementedError(
                        f"Conversion non prise en charge pour: {src_ext.upper()} -> {dst_ext.upper()}"
                    )

            if task.is_cancelled:
                task.status = "Annulé"
            elif success:
                task.status = "Terminé"
                task.progress = 100.0
            else:
                task.status = "Erreur"

        except Exception as e:
            task.status = "Erreur"
            task.error_message = str(e)

        if on_finish:
            on_finish(task)

"""
GLC CONVERTER — Moteur Exclusif HTML / Animations / WebGL vers Vraie Vidéo
Éditeur: GRAN LAKU COMPANY | https://granlaku.com/glcconverter
"""
import os
import sys
import time
import subprocess
from pathlib import Path
from typing import Optional, Callable

import numpy as np
from PIL import Image
import av

from PySide6.QtCore import QUrl, QEventLoop, QTimer, QSize
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings

from .codec_policy import add_video_stream

class HtmlVideoEngine:
    """
    Transforme n'importe quelle page web animée (CSS, Canvas 2D, Three.js, GSAP, WebGL)
    en véritable vidéo H.264 / ProRes sans aucune saccade via Horloge Virtuelle Déterministe.
    Exécute le rendu dans un sous-processus isolé pour garantir une fluidité totale de l'UI
    sans aucun gel (« Not Responding »).
    """

    CLOCK_SHIM_JS = """
    (function() {
        if (window.__glc_clock_injected) return;
        window.__glc_clock_injected = true;
        
        window.__glc_time = 0;
        let rafCallbacks = [];

        window.performance.now = function() {
            return window.__glc_time;
        };
        Date.now = function() {
            return 1700000000000 + window.__glc_time;
        };

        window.requestAnimationFrame = function(callback) {
            rafCallbacks.push(callback);
            return rafCallbacks.length;
        };

        window.__glc_advance_frame = function(dt) {
            window.__glc_time += dt;
            const cbs = rafCallbacks.slice();
            rafCallbacks = [];
            for (let i = 0; i < cbs.length; i++) {
                try {
                    cbs[i](window.__glc_time);
                } catch(e) {
                    console.error("Frame callback error:", e);
                }
            }
            return window.__glc_time;
        };
    })();
    """

    @classmethod
    def convert_html_to_video(
        cls,
        html_file_path: str,
        output_video_path: str,
        duration_sec: Optional[float] = None,
        fps: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        crf: int = 16,
        audio_path: Optional[str] = None,
        progress_callback: Optional[Callable[[float, float, str], None]] = None,
        cancel_check: Optional[Callable[[], bool]] = None
    ) -> bool:
        """
        Rend de manière déterministe chaque trame de la page web et assemble une vraie vidéo MP4
        avec synchronisation audio complète (voix, musique et effets sonores) en qualité Ultra-HD.
        Exécute le moteur dans un sous-processus isolé dédié pour garantir une fluidité 100%
        indépendante sans aucun gel d'interface (« Not Responding »).
        """
        # Auto-détection intelligente des métadonnées (durée réelle, dimensions, audio)
        from .html_detector import HtmlDetector
        detected = HtmlDetector.detect_html_metadata(html_file_path)

        if duration_sec is None or duration_sec == 5.0:
            if detected.get("duration") and detected["duration"] > 0:
                duration_sec = detected["duration"]
            else:
                duration_sec = 5.0

        if fps is None or fps == 60:
            if detected.get("fps"):
                fps = detected["fps"]
            else:
                fps = 30

        if width is None or height is None:
            if detected.get("width") and detected.get("height"):
                width = detected["width"]
                height = detected["height"]
            else:
                width = 1920
                height = 1080

        if not audio_path and detected.get("audio_path"):
            audio_path = detected["audio_path"]

        project_root = Path(__file__).resolve().parent.parent.parent
        env = os.environ.copy()
        existing_pp = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = str(project_root) + (os.pathsep + existing_pp if existing_pp else "")

        # Exécution dans un sous-processus isolé indépendant en Haute Fidélité Studio
        # Version installée (PyInstaller) : sys.executable est GLC CONVERTER.exe, qui lance
        # le moteur quand il reçoit --glc-render-html (voir main.py).
        if getattr(sys, "frozen", False):
            launcher = [sys.executable, "--glc-render-html"]
        else:
            launcher = [sys.executable, "-m", "src.core.html_video_renderer"]
        cmd = launcher + [
            "--input", str(html_file_path),
            "--output", str(output_video_path),
            "--duration", str(duration_sec),
            "--fps", str(fps),
            "--width", str(width),
            "--height", str(height),
            "--crf", str(crf),
            "--preset", "medium"
        ]
        if audio_path:
            cmd.extend(["--audio", str(audio_path)])

        try:
            creationflags = 0
            if sys.platform == "win32":
                creationflags = subprocess.CREATE_NO_WINDOW

            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                bufsize=1,
                cwd=str(project_root),
                env=env,
                creationflags=creationflags
            )

            got_done_success = False
            while True:
                if cancel_check and cancel_check():
                    proc.terminate()
                    try:
                        proc.wait(timeout=1.0)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                    if Path(output_video_path).exists():
                        try:
                            os.remove(output_video_path)
                        except Exception:
                            pass
                    return False

                line = proc.stdout.readline()
                if not line:
                    if proc.poll() is not None:
                        break
                    time.sleep(0.01)
                    continue

                line = line.strip()
                if line.startswith("PROGRESS:"):
                    parts = line.split(":")
                    if len(parts) >= 4:
                        try:
                            pct = float(parts[1])
                            fps_val = float(parts[2])
                            eta = f"{parts[3]}:{parts[4]}" if len(parts) >= 5 else parts[3]
                            if progress_callback:
                                progress_callback(pct, fps_val, eta)
                        except Exception:
                            pass

                elif line.startswith("DONE:SUCCESS"):
                    got_done_success = True
                    break

            try:
                proc.stdout.close()
                if proc.stderr:
                    proc.stderr.close()
            except Exception:
                pass

            try:
                proc.wait(timeout=3.0)
            except subprocess.TimeoutExpired:
                proc.kill()
                try:
                    proc.wait(timeout=1.0)
                except Exception:
                    pass

            out_exists = Path(output_video_path).exists() and (os.path.getsize(output_video_path) > 0)
            success = (got_done_success or proc.returncode == 0) and out_exists
            if success and progress_callback:
                progress_callback(100.0, 0.0, "00:00")
            return success

        except Exception as e:
            # Fallback direct en mémoire si l'invocation subprocess rencontre une contrainte
            print(f"[HtmlVideoEngine] Exécution directe in-process (fallback) : {e}")
            return cls._render_in_process(
                html_file_path=html_file_path,
                output_video_path=output_video_path,
                duration_sec=duration_sec,
                fps=fps,
                width=width,
                height=height,
                audio_path=audio_path,
                progress_callback=progress_callback,
                cancel_check=cancel_check
            )

    @classmethod
    def _render_in_process(
        cls,
        html_file_path: str,
        output_video_path: str,
        duration_sec: float = 5.0,
        fps: int = 60,
        width: int = 1920,
        height: int = 1080,
        audio_path: Optional[str] = None,
        progress_callback: Optional[Callable[[float, float, str], None]] = None,
        cancel_check: Optional[Callable[[], bool]] = None
    ) -> bool:
        """Méthode de secours in-process pour les environnements de test direct."""
        app = QApplication.instance() or QApplication(sys.argv)

        view = QWebEngineView()
        view.settings().setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)
        view.settings().setAttribute(QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled, True)
        view.resize(width, height)
        view.move(-20000, -20000)
        view.show()

        resolved_path = Path(html_file_path).resolve()
        if resolved_path.exists():
            file_url = QUrl.fromLocalFile(str(resolved_path))
        else:
            file_url = QUrl(html_file_path)

        load_loop = QEventLoop()
        view.loadFinished.connect(lambda ok: load_loop.quit())
        
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(load_loop.quit)
        timer.start(10000)
        
        view.load(file_url)
        load_loop.exec()

        view.page().runJavaScript(cls.CLOCK_SHIM_JS)

        wait_loop = QEventLoop()
        QTimer.singleShot(150, wait_loop.quit)
        wait_loop.exec()

        total_frames = max(1, int(duration_sec * fps))
        dt_ms = 1000.0 / fps

        out_container = av.open(output_video_path, mode="w")
        out_ext = Path(output_video_path).suffix.lower().lstrip(".")
        codec = "prores" if out_ext == "mov" else ("vp9" if out_ext == "webm" else "h264")
        # Encodeur sans GPL : carte graphique d'abord, puis repli libre selon le conteneur
        vstream, _encoder, video_pix_fmt = add_video_stream(
            out_container, codec, out_ext, width, height, fps, crf=18
        )

        astream = None
        in_audio = None
        resampler = None
        if audio_path and Path(audio_path).exists():
            try:
                in_audio = av.open(audio_path)
                if in_audio.streams.audio:
                    astream = out_container.add_stream("aac", rate=48000)
                    astream.layout = "stereo"
                    astream.bit_rate = 192000
                    resampler = av.AudioResampler(format="fltp", layout="stereo", rate=48000)
            except Exception:
                astream = None
                in_audio = None

        start_time = time.time()

        for frame_idx in range(total_frames):
            if cancel_check and cancel_check():
                out_container.close()
                view.close()
                view.deleteLater()
                if Path(output_video_path).exists():
                    os.remove(output_video_path)
                return False

            step_loop = QEventLoop()
            step_timer = QTimer()
            step_timer.setSingleShot(True)
            step_timer.timeout.connect(step_loop.quit)
            step_timer.start(500)

            view.page().runJavaScript(
                f"window.__glc_advance_frame({dt_ms});",
                lambda res: step_loop.quit()
            )
            step_loop.exec()

            app.processEvents()

            pix = view.grab()
            qimg = pix.toImage().convertToFormat(QImage.Format.Format_RGBA8888)
            if qimg.width() != width or qimg.height() != height:
                qimg = qimg.scaled(width, height)

            ptr = qimg.bits()
            arr = np.frombuffer(ptr, dtype=np.uint8).reshape((height, width, 4))
            
            video_frame = av.VideoFrame.from_ndarray(arr, format="rgba")
            video_frame = video_frame.reformat(format=video_pix_fmt)
            video_frame.pts = frame_idx

            for packet in vstream.encode(video_frame):
                out_container.mux(packet)

            if progress_callback and (frame_idx % 2 == 0 or frame_idx == total_frames - 1):
                elapsed = max(0.01, time.time() - start_time)
                curr_fps = (frame_idx + 1) / elapsed
                pct = ((frame_idx + 1) / total_frames) * 100.0
                
                rem_sec = int((total_frames - (frame_idx + 1)) / curr_fps) if curr_fps > 0 else 0
                m, s = divmod(rem_sec, 60)
                eta_str = f"{m:02d}:{s:02d}"

                progress_callback(pct, curr_fps, eta_str)

        for packet in vstream.encode():
            out_container.mux(packet)

        if astream and in_audio and resampler:
            try:
                samples_encoded = 0
                max_samples = int(duration_sec * 48000)
                for aframe in in_audio.decode(audio=0):
                    for rframe in resampler.resample(aframe):
                        for packet in astream.encode(rframe):
                            out_container.mux(packet)
                        samples_encoded += rframe.samples
                    if samples_encoded >= max_samples:
                        break
                for rframe in resampler.resample(None):
                    for packet in astream.encode(rframe):
                        out_container.mux(packet)
                for packet in astream.encode():
                    out_container.mux(packet)
            except Exception:
                pass
            finally:
                try:
                    in_audio.close()
                except Exception:
                    pass

        out_container.close()
        view.close()
        view.deleteLater()

        if progress_callback:
            progress_callback(100.0, 0.0, "00:00")

        return True

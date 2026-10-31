"""
GLC CONVERTER — Processus Isolé de Rendu Déterministe HTML vers Vidéo
Éditeur: GRAN LAKU COMPANY | https://granlaku.com/glcconverter

Ce script s'exécute dans son propre processus Python indépendant avec son propre thread GUI,
permettant à QWebEngineView de capturer chaque trame WebGL/Canvas sans bloquer l'application
principale et sans aucun gel (« Not Responding »).
"""
import sys
import os
import time
import argparse
from pathlib import Path
from typing import Optional

import numpy as np
import av
from PIL import Image

from PySide6.QtCore import Qt, QUrl, QEventLoop, QTimer
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings

from .html_detector import HtmlDetector
from .codec_policy import add_video_stream

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

def render_html_to_video(
    input_path: str,
    output_path: str,
    duration_sec: float = 5.0,
    fps: int = 60,
    width: int = 1920,
    height: int = 1080,
    crf: int = 16,
    preset: str = "medium",
    audio_path: Optional[str] = None
) -> int:
    """Effectue le rendu déterministe haute fidélité d'un fichier HTML en vidéo MP4 Ultra-HD."""
    # Désactiver les avertissements graphiques Chromium superflus et forcer l'échelle 1.0
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "0"
    os.environ["QT_SCALE_FACTOR"] = "1"
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--no-sandbox --disable-logging --disable-gpu-watchdog"

    # Détection automatique intelligente des paramètres si non spécifiés
    try:
        detected = HtmlDetector.detect_html_metadata(input_path)
        if not audio_path and detected.get("audio_path"):
            audio_path = detected["audio_path"]
        if (duration_sec is None or duration_sec == 5.0) and detected.get("duration") and detected["duration"] > 5.0:
            duration_sec = detected["duration"]
        if (fps == 60) and detected.get("fps") and detected["fps"] != 60:
            fps = detected["fps"]
    except Exception as e:
        sys.stderr.write(f"[HtmlRenderer] Metadata detect notice: {e}\n")

    app = QApplication.instance() or QApplication(sys.argv)

    view = QWebEngineView()
    view.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint)
    view.settings().setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)
    view.settings().setAttribute(QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled, True)
    view.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
    view.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
    view.resize(width, height)
    view.page().setZoomFactor(1.0)
    view.move(-15000, -15000)
    view.show()

    s_input = str(input_path).strip()
    is_http_url = s_input.startswith("http://") or s_input.startswith("https://")
    if is_http_url:
        file_url = QUrl(s_input)
    else:
        resolved_path = Path(s_input).resolve()
        if resolved_path.exists():
            file_url = QUrl.fromLocalFile(str(resolved_path))
        else:
            file_url = QUrl(s_input)

    # Kadans & Rendu Déterministe : Toujours ajouter le fragment '#render'
    # pour que composition.html masque et supprime #kplay_center et active window.__seek
    if not file_url.fragment():
        file_url.setFragment("render")

    # 1. Chargement de la page avec boucle locale sécurisée
    load_loop = QEventLoop()
    timeout_timer = QTimer()
    timeout_timer.setSingleShot(True)
    
    def on_load_finished(ok):
        timeout_timer.stop()
        load_loop.quit()

    view.loadFinished.connect(on_load_finished)
    timeout_timer.timeout.connect(load_loop.quit)
    timeout_timer.start(8000)
    
    view.load(file_url)
    load_loop.exec()
    timeout_timer.stop()

    # 2. Injection du shim d'horloge déterministe et styles de netteté CSS
    view.page().runJavaScript(CLOCK_SHIM_JS)
    css_injection = f"""
    (function() {{
        let s = document.createElement('style');
        s.innerHTML = `
            html, body, svg {{
                width: {width}px !important;
                height: {height}px !important;
                margin: 0 !important;
                padding: 0 !important;
                overflow: hidden !important;
                image-rendering: -webkit-optimize-contrast !important;
                -webkit-font-smoothing: antialiased !important;
            }}
            /* Masquer absolument le bouton play central s'il subsiste dans le DOM */
            #kplay_center, .kplay_center, #krange, #ktime, #kplay {{
                display: none !important;
                visibility: hidden !important;
            }}
        `;
        if (document.head) {{
            document.head.appendChild(s);
        }} else if (document.documentElement) {{
            document.documentElement.appendChild(s);
        }}
        if (document.documentElement && document.documentElement.tagName.toLowerCase() === 'svg') {{
            document.documentElement.setAttribute('width', '{width}');
            document.documentElement.setAttribute('height', '{height}');
        }}
        // Activer les attributs is-render
        if (document.documentElement) document.documentElement.classList.add('is-render');
        if (document.body) {{
            document.body.classList.add('is-render');
            document.body.setAttribute('data-render', 'true');
        }}
        const kpc = document.getElementById('kplay_center');
        if (kpc) {{
            kpc.style.display = 'none';
            try {{ kpc.remove(); }} catch(e) {{}}
        }}
        if (typeof window.seekSync === 'function') {{
            try {{ window.seekSync(0); }} catch(e) {{}}
        }}
    }})();
    """
    view.page().runJavaScript(css_injection)

    # Stabilisation initiale (150ms)
    wait_loop = QEventLoop()
    QTimer.singleShot(150, wait_loop.quit)
    wait_loop.exec()

    total_frames = max(1, int(duration_sec * fps))
    dt_ms = 1000.0 / fps

    # 3. Initialisation du conteneur PyAV avec flux vidéo et audio Ultra-HD
    out_dir = Path(output_path).parent
    out_dir.mkdir(parents=True, exist_ok=True)

    out_container = av.open(output_path, mode="w")
    out_ext = Path(output_path).suffix.lower().lstrip(".")
    codec = "prores" if out_ext == "mov" else ("vp9" if out_ext == "webm" else "h264")
    # Encodeur sans GPL : carte graphique d'abord, puis repli libre selon le conteneur
    vstream, _encoder, video_pix_fmt = add_video_stream(
        out_container, codec, out_ext, width, height, fps, crf=min(16, crf)
    )

    # Configuration du flux audio si une piste est détectée (voix / musique / ambiance)
    astream = None
    in_audio = None
    resampler = None
    if audio_path and Path(audio_path).exists():
        try:
            in_audio = av.open(audio_path)
            if in_audio.streams.audio:
                audio_codec = "aac"
                if output_path.lower().endswith(".webm"):
                    audio_codec = "libopus"
                astream = out_container.add_stream(audio_codec, rate=48000)
                astream.layout = "stereo"
                astream.bit_rate = 192000
                resampler = av.AudioResampler(format="fltp", layout="stereo", rate=48000)
        except Exception as e:
            astream = None
            in_audio = None

    start_time = time.time()

    # 4. Rendu trame par trame
    for frame_idx in range(total_frames):
        # Avance du temps JavaScript avec arrêt propre du timer
        step_loop = QEventLoop()
        step_timer = QTimer()
        step_timer.setSingleShot(True)

        def on_step_done(res=None):
            step_timer.stop()
            step_loop.quit()

        step_timer.timeout.connect(step_loop.quit)
        step_timer.start(400)

        current_t_sec = frame_idx / fps
        view.page().runJavaScript(
            f"""
            (function() {{
                const t = {current_t_sec:.6f};
                if (typeof window.__seek === 'function') {{
                    try {{ window.__seek(t); }} catch(e) {{}}
                }} else if (typeof window.seekSync === 'function') {{
                    try {{ window.seekSync(t); }} catch(e) {{}}
                }}
                if (typeof window.__glc_advance_frame === 'function') {{
                    try {{ window.__glc_advance_frame({dt_ms}); }} catch(e) {{}}
                }}
            }})();
            """,
            on_step_done
        )
        step_loop.exec()
        step_timer.stop()

        app.processEvents()

        # Capture haute fidélité
        pix = view.grab()
        qimg = pix.toImage().convertToFormat(QImage.Format.Format_RGBA8888)
        if qimg.width() != width or qimg.height() != height:
            qimg = qimg.scaled(width, height, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)

        ptr = qimg.bits()
        arr = np.frombuffer(ptr, dtype=np.uint8).reshape((height, width, 4))

        video_frame = av.VideoFrame.from_ndarray(arr, format="rgba")
        try:
            video_frame = video_frame.reformat(format=video_pix_fmt, interpolation="LANCZOS")
        except Exception:
            video_frame = video_frame.reformat(format=video_pix_fmt)
        video_frame.pts = frame_idx

        for packet in vstream.encode(video_frame):
            out_container.mux(packet)

        # Rapport de progression temps réel sur stdout pour le processus parent
        if frame_idx % 2 == 0 or frame_idx == total_frames - 1:
            elapsed = max(0.01, time.time() - start_time)
            curr_fps = (frame_idx + 1) / elapsed
            pct = ((frame_idx + 1) / total_frames) * 100.0
            
            rem_sec = int((total_frames - (frame_idx + 1)) / curr_fps) if curr_fps > 0 else 0
            m, s = divmod(rem_sec, 60)
            eta_str = f"{m:02d}:{s:02d}"

            sys.stdout.write(f"PROGRESS:{pct:.2f}:{curr_fps:.1f}:{eta_str}\n")
            sys.stdout.flush()

    # Flush final de l'encodeur vidéo
    for packet in vstream.encode():
        out_container.mux(packet)

    # 5. Encodage et multiplexage du flux audio synchronisé
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
        except Exception as e:
            sys.stderr.write(f"[HtmlRenderer] Audio encoding error: {e}\n")
            sys.stderr.flush()
        finally:
            try:
                in_audio.close()
            except Exception:
                pass

    out_container.close()
    try:
        view.close()
        view.deleteLater()
    except Exception:
        pass

    sys.stdout.write("PROGRESS:100.00:0.0:00:00\n")
    sys.stdout.write("DONE:SUCCESS\n")
    sys.stdout.flush()
    return 0

def main():
    parser = argparse.ArgumentParser(description="GLC HTML to Video Subprocess Renderer")
    parser.add_argument("--input", required=True, help="Chemin du fichier HTML source")
    parser.add_argument("--output", required=True, help="Chemin du fichier vidéo cible")
    parser.add_argument("--duration", type=float, default=5.0, help="Durée en secondes")
    parser.add_argument("--fps", type=int, default=60, help="Cadence d'images (FPS)")
    parser.add_argument("--width", type=int, default=1920, help="Largeur en pixels")
    parser.add_argument("--height", type=int, default=1080, help="Hauteur en pixels")
    parser.add_argument("--crf", type=int, default=18, help="Qualité CRF (12-28)")
    parser.add_argument("--preset", default="veryfast", help="Conservé pour compatibilité ; l'encodeur est choisi par codec_policy (sans GPL)")
    parser.add_argument("--audio", default=None, help="Chemin de la piste audio maîtresse à synchroniser")

    args = parser.parse_args()
    try:
        ret = render_html_to_video(
            input_path=args.input,
            output_path=args.output,
            duration_sec=args.duration,
            fps=args.fps,
            width=args.width,
            height=args.height,
            crf=args.crf,
            preset=args.preset,
            audio_path=args.audio
        )
        # Sortie instantanée sans blocage dans les threads atexit de Chromium
        os._exit(ret)
    except Exception as e:
        sys.stderr.write(f"ERROR: {e}\n")
        sys.stderr.flush()
        os._exit(1)

if __name__ == "__main__":
    main()

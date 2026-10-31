"""
GLC CONVERTER — Moteur Vidéo Haute Performance (Support Standard, 4K, 8K et 12K)
Éditeur: GRAN LAKU COMPANY | https://granlaku.com/glcconverter
"""
import os
import time
from pathlib import Path
from typing import Callable, Optional, Dict, Any
from PIL import Image
import av
from . import codec_policy

class VideoEngine:
    """Moteur d'encodage et de transcodage vidéo avec accélération GPU et support jusqu'au 12K."""

    @classmethod
    def convert_video(
        cls,
        input_path: str,
        output_path: str,
        target_codec: str = "h264",
        crf: int = 22,
        bitrate: Optional[str] = None,
        resolution: Optional[str] = None, # ex: "12288x6480" (12K), "7680x4320" (8K), "3840x2160" (4K)
        fps: Optional[float] = None,
        hw_accel: bool = True,
        progress_callback: Optional[Callable[[float, float, str], None]] = None,
        cancel_check: Optional[Callable[[], bool]] = None
    ) -> bool:
        """
        Transcode un fichier vidéo source vers la destination demandée avec support des formats jusqu'à 12K.
        """
        out_ext = Path(output_path).suffix.lower().lstrip(".")
        out_width, out_height = cls._output_size(input_path, resolution)

        # Encodeurs sans GPL (carte graphique d'abord, puis logiciels libres), réellement
        # ouvrables à la taille de sortie : un H.264 trop grand pour le GPU bascule seul vers
        # HEVC / AV1 matériels puis SVT-AV1 ou ProRes selon le conteneur.
        candidates = codec_policy.usable_video_encoders(
            target_codec, out_ext, out_width, out_height, allow_hw=hw_accel
        )
        if not candidates:
            raise RuntimeError(
                f"Aucun encodeur sans GPL disponible pour .{out_ext} en {out_width}x{out_height}."
            )

        last_error = None
        for encoder_name, pix_fmt in candidates:
            try:
                success = cls._do_transcode(
                    input_path=input_path,
                    output_path=output_path,
                    encoder_name=encoder_name,
                    pix_fmt=pix_fmt,
                    crf=crf,
                    bitrate=bitrate,
                    resolution=resolution,
                    fps=fps,
                    progress_callback=progress_callback,
                    cancel_check=cancel_check
                )
                if success:
                    return True
            except Exception as e:
                last_error = e
                if Path(output_path).exists():
                    try:
                        os.remove(output_path)
                    except Exception:
                        pass
                continue

        if last_error:
            raise last_error
        return False

    @staticmethod
    def _output_size(input_path: str, resolution: Optional[str]):
        """Taille de sortie (paire) : résolution demandée ou celle de la source."""
        width = height = 0
        if resolution and "x" in resolution:
            try:
                rw, rh = resolution.lower().split("x")
                width, height = int(rw), int(rh)
            except Exception:
                width = height = 0
        if not width or not height:
            with av.open(input_path) as probe:
                if not probe.streams.video:
                    raise ValueError("Aucun flux vidéo détecté dans le fichier source.")
                ctx = probe.streams.video[0].codec_context
                width, height = ctx.width, ctx.height
        return (width // 2) * 2, (height // 2) * 2

    @staticmethod
    def _do_transcode(
        input_path: str,
        output_path: str,
        encoder_name: str,
        pix_fmt: str,
        crf: int,
        bitrate: Optional[str],
        resolution: Optional[str],
        fps: Optional[float],
        progress_callback: Optional[Callable[[float, float, str], None]],
        cancel_check: Optional[Callable[[], bool]]
    ) -> bool:
        input_container = av.open(input_path)
        in_video_stream = input_container.streams.video[0] if input_container.streams.video else None
        in_audio_stream = input_container.streams.audio[0] if input_container.streams.audio else None

        if not in_video_stream:
            input_container.close()
            raise ValueError("Aucun flux vidéo détecté dans le fichier source.")

        total_frames = in_video_stream.frames
        duration_sec = float(input_container.duration or 0) / av.time_base if input_container.duration else 0

        # Résolution de sortie
        out_width = in_video_stream.codec_context.width
        out_height = in_video_stream.codec_context.height
        if resolution and "x" in resolution:
            try:
                rw, rh = resolution.lower().split("x")
                out_width = int(rw)
                out_height = int(rh)
            except Exception:
                pass

        # Dimensions paires requises
        out_width = (out_width // 2) * 2
        out_height = (out_height // 2) * 2

        output_container = av.open(output_path, mode="w")
        target_rate = fps or in_video_stream.average_rate or 30

        out_video_stream = output_container.add_stream(encoder_name, rate=target_rate)
        out_video_stream.width = out_width
        out_video_stream.height = out_height
        out_video_stream.pix_fmt = pix_fmt

        # Débit cible Haute Fidélité selon la résolution (1080p → 12K)
        target_bitrate = codec_policy.default_bitrate(out_width, out_height)

        # Options de qualité adaptées au codec et à la résolution (8K / 12K)
        if bitrate:
            try:
                b_str = bitrate.lower()
                if b_str.endswith("m"):
                    out_video_stream.bit_rate = int(float(b_str[:-1]) * 1_000_000)
                elif b_str.endswith("k"):
                    out_video_stream.bit_rate = int(float(b_str[:-1]) * 1_000)
                else:
                    out_video_stream.bit_rate = int(b_str)
            except Exception:
                out_video_stream.bit_rate = target_bitrate
        else:
            opts, enc_bitrate = codec_policy.encoder_options(
                encoder_name, out_width, out_height, crf, target_bitrate
            )
            if opts:
                out_video_stream.options = opts
            if enc_bitrate:
                out_video_stream.bit_rate = enc_bitrate

        # Configuration audio compatible conteneur
        out_ext = Path(output_path).suffix.lower().lstrip(".")
        out_audio_stream = None
        if in_audio_stream:
            try:
                if out_ext == "webm":
                    out_audio_stream = output_container.add_stream("libopus", rate=48000)
                else:
                    out_audio_stream = output_container.add_stream("aac", rate=48000)
                out_audio_stream.channels = 2
                out_audio_stream.bit_rate = 192000
            except Exception:
                pass

        start_time = time.time()
        processed_frames = 0
        target_fmt = pix_fmt

        for frame in input_container.decode(video=0):
            if cancel_check and cancel_check():
                output_container.close()
                input_container.close()
                return False

            if frame.width != out_width or frame.height != out_height or frame.format.name != target_fmt:
                try:
                    frame = frame.reformat(width=out_width, height=out_height, format=target_fmt, interpolation="LANCZOS")
                except Exception:
                    frame = frame.reformat(width=out_width, height=out_height, format=target_fmt)

            for packet in out_video_stream.encode(frame):
                output_container.mux(packet)

            processed_frames += 1

            if progress_callback and processed_frames % 5 == 0:
                elapsed = time.time() - start_time
                fps_rate = processed_frames / elapsed if elapsed > 0 else 0
                
                percent = 0.0
                if total_frames and total_frames > 0:
                    percent = min(99.0, (processed_frames / total_frames) * 100.0)
                elif duration_sec > 0 and frame.time:
                    percent = min(99.0, (float(frame.time) / duration_sec) * 100.0)

                eta_str = "--:--"
                if fps_rate > 0 and total_frames:
                    rem_sec = int((total_frames - processed_frames) / fps_rate)
                    m, s = divmod(rem_sec, 60)
                    eta_str = f"{m:02d}:{s:02d}"

                progress_callback(percent, fps_rate, eta_str)

        # Flush vidéo
        for packet in out_video_stream.encode():
            output_container.mux(packet)

        # Audio mux
        if in_audio_stream and out_audio_stream:
            input_container.seek(0)
            for aframe in input_container.decode(audio=0):
                if cancel_check and cancel_check():
                    break
                for apacket in out_audio_stream.encode(aframe):
                    output_container.mux(apacket)
            
            for apacket in out_audio_stream.encode():
                output_container.mux(apacket)

        output_container.close()
        input_container.close()

        if progress_callback:
            progress_callback(100.0, 0, "00:00")

        return True

    @classmethod
    def image_to_video(
        cls,
        image_path: str,
        output_path: str,
        duration_sec: float = 5.0,
        fps: int = 30,
        resolution: Optional[str] = None,
        progress_callback: Optional[Callable[[float, float, str], None]] = None,
        cancel_check: Optional[Callable[[], bool]] = None
    ) -> bool:
        """
        Convertit une image statique (PNG, JPG, WebP, SVG, etc.) en un fichier vidéo
        MP4/MOV/WebM fluide avec support de résolution jusqu'en 12K.
        """
        in_p = Path(image_path)
        out_p = Path(output_path)
        out_ext = out_p.suffix.lower().lstrip(".")

        # Chargement de l'image via Pillow
        pil_img = Image.open(str(in_p))
        if pil_img.mode != "RGB":
            pil_img = pil_img.convert("RGB")

        # Calcul des dimensions
        w, h = pil_img.width, pil_img.height
        if resolution and "x" in resolution:
            try:
                rw, rh = resolution.lower().split("x")
                w, h = int(rw), int(rh)
            except Exception:
                pass

        # Dimensions paires
        w = (w // 2) * 2
        h = (h // 2) * 2
        if pil_img.size != (w, h):
            pil_img = pil_img.resize((w, h), Image.Resampling.LANCZOS)

        # Encodeur sans GPL (ProRes en .mov/.mkv à partir du 8K, sinon H.264 matériel ou repli libre)
        codec = "prores" if (out_ext in ["mov", "mkv"] and w >= 7680) else "h264"
        output_container = av.open(str(out_p), mode="w")
        stream, _encoder, pix_fmt = codec_policy.add_video_stream(
            output_container, codec, out_ext, w, h, fps, crf=18
        )

        total_frames = int(duration_sec * fps)
        base_frame = av.VideoFrame.from_image(pil_img).reformat(format=pix_fmt)

        for i in range(total_frames):
            if cancel_check and cancel_check():
                output_container.close()
                if out_p.exists():
                    os.remove(str(out_p))
                return False

            base_frame.pts = i
            for packet in stream.encode(base_frame):
                output_container.mux(packet)

            if progress_callback and total_frames > 0:
                pct = ((i + 1) / total_frames) * 100.0
                progress_callback(pct, 0.0, "--:--")

        for packet in stream.encode():
            output_container.mux(packet)
        output_container.close()

        if progress_callback:
            progress_callback(100.0, 0.0, "00:00")
        return True

    @classmethod
    def video_to_image(
        cls,
        video_path: str,
        output_path: str,
        progress_callback: Optional[Callable[[float, float, str], None]] = None
    ) -> bool:
        """Extrait la première frame clé d'une vidéo et l'enregistre en image."""
        if progress_callback:
            progress_callback(20.0, 0.0, "--:--")

        with av.open(video_path) as container:
            if not container.streams.video:
                raise ValueError("Aucun flux vidéo dans le fichier.")
            vstream = container.streams.video[0]
            for frame in container.decode(vstream):
                img = frame.to_image()
                img.save(output_path)
                if progress_callback:
                    progress_callback(100.0, 0.0, "00:00")
                return True
        return False

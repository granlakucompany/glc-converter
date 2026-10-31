"""
GLC CONVERTER — Moteur Audio & Extraction Sonore
Éditeur: GRAN LAKU COMPANY | https://granlaku.com/glcconverter
"""
import os
import time
from pathlib import Path
from typing import Callable, Optional
import av

class AudioEngine:
    """Gère la conversion de fichiers audio et l'extraction de bandes sonores vidéo."""

    CODEC_MAP = {
        "mp3": "mp3",
        "wav": "pcm_s16le",
        "flac": "flac",
        "aac": "aac",
        "m4a": "aac",
        "ogg": "libvorbis",
        "opus": "libopus"
    }

    @classmethod
    def convert_audio(
        cls,
        input_path: str,
        output_path: str,
        target_format: str = "mp3",
        bitrate: str = "320k",
        sample_rate: int = 44100,
        progress_callback: Optional[Callable[[float, float, str], None]] = None,
        cancel_check: Optional[Callable[[], bool]] = None
    ) -> bool:
        """Convertit ou extrait une piste audio vers le format cible."""
        target_fmt = target_format.lower().lstrip(".")
        codec_name = cls.CODEC_MAP.get(target_fmt, "mp3")

        input_container = av.open(input_path)
        if not input_container.streams.audio:
            input_container.close()
            raise ValueError("Aucun flux audio détecté dans le fichier source.")

        in_audio_stream = input_container.streams.audio[0]
        duration_sec = float(input_container.duration or 0) / av.time_base if input_container.duration else 0

        output_container = av.open(output_path, mode="w")
        
        try:
            out_audio_stream = output_container.add_stream(codec_name, rate=sample_rate)
        except Exception:
            out_audio_stream = output_container.add_stream("mp3", rate=sample_rate)

        out_audio_stream.channels = 2

        # Bitrate
        try:
            b_val = bitrate.lower()
            if b_val.endswith("k"):
                out_audio_stream.bit_rate = int(float(b_val[:-1]) * 1000)
            else:
                out_audio_stream.bit_rate = int(b_val)
        except Exception:
            out_audio_stream.bit_rate = 320000

        # Resampler pour standardiser la fréquence et le format de sample
        resampler = av.AudioResampler(
            format=out_audio_stream.format,
            layout="stereo",
            rate=sample_rate
        )

        start_time = time.time()
        for frame in input_container.decode(audio=0):
            if cancel_check and cancel_check():
                output_container.close()
                input_container.close()
                if Path(output_path).exists():
                    os.remove(output_path)
                return False

            for r_frame in resampler.resample(frame):
                for packet in out_audio_stream.encode(r_frame):
                    output_container.mux(packet)

            if progress_callback and frame.time and duration_sec > 0:
                percent = min(99.0, (float(frame.time) / duration_sec) * 100.0)
                progress_callback(percent, 0.0, "--:--")

        for packet in out_audio_stream.encode():
            output_container.mux(packet)

        output_container.close()
        input_container.close()

        if progress_callback:
            progress_callback(100.0, 0.0, "00:00")

        return True

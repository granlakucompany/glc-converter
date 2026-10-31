"""
GLC CONVERTER — Détection Réelle de l'Accélération Matérielle GPU
Éditeur: GRAN LAKU COMPANY | https://granlaku.com/glcconverter
"""
import os
import multiprocessing
from fractions import Fraction
import av

class HardwareDetector:
    """Détecte les capacités réelles d'encodage matériel de la machine."""
    
    _instance = None
    
    def __init__(self):
        self.cpu_cores = multiprocessing.cpu_count()
        self.available_codecs = av.codec.codecs_available
        self.nvenc_available = False
        self.qsv_available = False
        self.amf_available = False
        self._probe_gpu_encoders()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _test_codec_open(self, codec_name: str) -> bool:
        """Tente d'ouvrir réellement le codec pour vérifier si le GPU physique est présent."""
        if codec_name not in self.available_codecs:
            return False
        try:
            ctx = av.CodecContext.create(codec_name, "w")
            ctx.width = 320
            ctx.height = 240
            ctx.pix_fmt = "yuv420p"
            ctx.time_base = Fraction(1, 30)
            ctx.open()
            return True
        except Exception:
            return False

    def _probe_gpu_encoders(self):
        # Vérification NVIDIA NVENC
        self.nvenc_available = self._test_codec_open("h264_nvenc")
        
        # Vérification Intel QuickSync (QSV)
        self.qsv_available = self._test_codec_open("h264_qsv")
        
        # Vérification AMD AMF
        self.amf_available = self._test_codec_open("h264_amf")

    def get_preferred_video_encoder(self, target_codec: str, allow_hw: bool = True) -> str:
        """
        Retourne l'encodeur optimal validé matériellement ou logiciel.
        """
        target = target_codec.lower()
        if allow_hw:
            if target in ["h264", "avc"]:
                if self.nvenc_available:
                    return "h264_nvenc"
                if self.qsv_available:
                    return "h264_qsv"
                if self.amf_available:
                    return "h264_amf"
            elif target in ["h265", "hevc"]:
                if self.nvenc_available and self._test_codec_open("hevc_nvenc"):
                    return "hevc_nvenc"
                if self.qsv_available and self._test_codec_open("hevc_qsv"):
                    return "hevc_qsv"
                if self.amf_available and self._test_codec_open("hevc_amf"):
                    return "hevc_amf"

        # Replis logiciels sans GPL (libx264 / libx265 interdits : voir codec_policy)
        from . import codec_policy
        chain = codec_policy.video_encoder_chain(target, "mkv", allow_hw=False)
        return chain[0] if chain else "mpeg4"

    def get_summary_text(self) -> str:
        lines = [f"Processeur: {self.cpu_cores} threads"]
        gpu = []
        if self.nvenc_available: gpu.append("NVIDIA NVENC")
        if self.qsv_available: gpu.append("Intel QuickSync")
        if self.amf_available: gpu.append("AMD AMF")

        if gpu:
            lines.append("Accélération GPU: " + " | ".join(gpu))
        else:
            lines.append("Accélération GPU: Mode CPU Multi-Cœurs haute précision")
        return "\n".join(lines)

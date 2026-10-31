"""
GLC CONVERTER — Moteur Document (PDF, DOCX, TXT, EPUB)
Éditeur: GRAN LAKU COMPANY | https://granlaku.com/glcconverter
"""
import os
from pathlib import Path
from typing import Optional, Callable
import pypdfium2 as pdfium
from PIL import Image

try:
    import docx
    DOCX_AVAILABLE = True
except Exception:
    DOCX_AVAILABLE = False

class DocEngine:
    """Gère la conversion de documents bureautiques et électroniques."""

    @classmethod
    def convert_document(
        cls,
        input_path: str,
        output_path: str,
        progress_callback: Optional[Callable[[float, float, str], None]] = None
    ) -> bool:
        """Convertit un document (ex: PDF vers Image, DOCX vers Texte ou PDF)."""
        in_p = Path(input_path)
        out_p = Path(output_path)
        ext_in = in_p.suffix.lower().lstrip(".")
        ext_out = out_p.suffix.lower().lstrip(".")

        if progress_callback:
            progress_callback(10.0, 0.0, "--:--")

        # Cas 1: PDF vers Images (PNG/JPG)
        if ext_in == "pdf" and ext_out in ["png", "jpg", "jpeg", "webp"]:
            pdf = pdfium.PdfDocument(str(in_p))
            n_pages = len(pdf)
            if n_pages == 0:
                raise ValueError("Le document PDF est vide.")

            # Rendu de la première page ou de toutes les pages
            page = pdf[0]
            pil_image = page.render(scale=2.0).to_pil()
            pil_image.save(str(out_p))

            if progress_callback:
                progress_callback(100.0, 0.0, "00:00")
            return True

        # Cas 2: DOCX vers Fichier Texte brut
        if ext_in == "docx" and ext_out in ["txt", "md"] and DOCX_AVAILABLE:
            doc = docx.Document(str(in_p))
            text_lines = [p.text for p in doc.paragraphs]
            with open(out_p, "w", encoding="utf-8") as f:
                f.write("\n\n".join(text_lines))

            if progress_callback:
                progress_callback(100.0, 0.0, "00:00")
            return True

        # Cas 3: Fichier Texte brut vers PDF via ReportLab
        if ext_in in ["txt", "md"] and ext_out == "pdf":
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas

            c = canvas.Canvas(str(out_p), pagesize=letter)
            width, height = letter
            y = height - 50

            with open(in_p, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    c.drawString(50, y, line.strip()[:90])
                    y -= 15
                    if y < 50:
                        c.showPage()
                        y = height - 50
            c.save()

            if progress_callback:
                progress_callback(100.0, 0.0, "00:00")
            return True

        raise NotImplementedError(f"Conversion {ext_in} -> {ext_out} non supportée directement.")

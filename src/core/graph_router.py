"""
GLC CONVERTER — Routage Dynamique de Conversion (Graph-Based Pathfinding)
Éditeur: GRAN LAKU COMPANY | https://granlaku.com/glcconverter
"""
from typing import List, Dict, Tuple, Optional
import heapq

class GraphRouter:
    """
    Modélise l'ensemble des conversions sous forme de graphe orienté pondéré.
    Calcule le chemin de conversion optimal (Dijkstra) pour passer d'un format A vers un format B.
    """

    def __init__(self):
        # Format Source -> List of (Format Cible, Coût Dégradation/Temps, Méthode)
        self.edges: Dict[str, List[Tuple[str, float, str]]] = {}
        self._build_default_graph()

    def add_edge(self, src: str, dst: str, weight: float, method: str):
        src, dst = src.lower(), dst.lower()
        if src not in self.edges:
            self.edges[src] = []
        self.edges[src].append((dst, weight, method))

    def _build_default_graph(self):
        # 1. Vidéo vers Vidéo
        video_formats = ["mp4", "mkv", "mov", "webm", "avi", "flv", "wmv", "ts", "prores"]
        for v1 in video_formats:
            for v2 in video_formats:
                if v1 != v2:
                    self.add_edge(v1, v2, 1.0, "video_transcode")

        # 2. Vidéo vers Audio (Extraction)
        audio_formats = ["mp3", "wav", "flac", "aac", "ogg", "opus", "m4a"]
        for v in video_formats:
            for a in audio_formats:
                self.add_edge(v, a, 1.2, "audio_extract")

        # 3. Audio vers Audio
        for a1 in audio_formats:
            for a2 in audio_formats:
                if a1 != a2:
                    cost = 1.0 if a2 in ["wav", "flac"] else 1.5
                    self.add_edge(a1, a2, cost, "audio_transcode")

        # 4. Images Raster vers Raster
        img_formats = ["png", "jpg", "jpeg", "webp", "avif", "heic", "tiff", "bmp"]
        for i1 in img_formats:
            for i2 in img_formats:
                if i1 != i2:
                    self.add_edge(i1, i2, 1.0, "image_convert")

        # 5. Vecteur SVG vers Raster
        for img in ["png", "jpg", "jpeg", "webp", "pdf"]:
            self.add_edge("svg", img, 1.0, "svg_rasterize")

        # 6. RAW vers Raster
        for raw in ["cr2", "nef", "arw", "dng"]:
            for img in ["tiff", "png", "jpg", "webp"]:
                self.add_edge(raw, img, 1.1, "raw_develop")

        # 7. Document PDF vers Image
        for img in ["png", "jpg", "webp"]:
            self.add_edge("pdf", img, 1.2, "pdf_render")

        # 8. HTML / Web vers Vidéo
        for vf in ["mp4", "mov", "webm"]:
            self.add_edge("html", vf, 1.5, "html_virtual_time_render")

        # 9. Document DOCX vers Texte & PDF
        self.add_edge("docx", "txt", 1.0, "docx_extract")
        self.add_edge("docx", "pdf", 2.0, "docx_to_pdf")
        self.add_edge("txt", "pdf", 1.2, "txt_to_pdf")

    def find_shortest_path(self, src: str, dst: str) -> Optional[List[Tuple[str, str, str]]]:
        """
        Trouve le chemin optimal avec l'algorithme de Dijkstra.
        Retourne une liste de triplets: (Source, Destination, Méthode)
        """
        src, dst = src.lower(), dst.lower()
        if src == dst:
            return []

        queue = [(0.0, src, [])]
        visited = set()

        while queue:
            cost, current, path = heapq.heappop(queue)

            if current == dst:
                return path

            if current in visited:
                continue
            visited.add(current)

            for neighbor, weight, method in self.edges.get(current, []):
                if neighbor not in visited:
                    heapq.heappush(queue, (cost + weight, neighbor, path + [(current, neighbor, method)]))

        return None

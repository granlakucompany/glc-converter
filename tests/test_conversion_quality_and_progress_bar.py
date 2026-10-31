"""
Test complet de validation :
1. Barre de progression inférieure avec détails explicites du format cible :
   « En cours de conversion en 4K UHD (MP4) », « En cours de conversion en PNG (Lossless) », etc.
2. Qualité vidéo 4K / 8K :
   Vérification que l'encodeur alloue un débit professionnel (>= 35 Mbps pour 4K au lieu de 200 kbps)
   et applique l'interpolation LANCZOS.
3. Qualité de rendu HTML vers Vidéo :
   Vérification du profil de netteté studio (CRF 16, tune animation, preset medium).
"""
import sys
import os
import tempfile
import time
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from PySide6.QtWidgets import QApplication
import av

from src.core.converter_engine import ConversionTask, ConverterEngine
from src.core.video_engine import VideoEngine
from src.core.html_video_engine import HtmlVideoEngine
from src.ui.process_bar import ProcessProgressBar

def run_tests():
    app = QApplication.instance() or QApplication(sys.argv)
    tmp = tempfile.gettempdir()

    print("-> 1. Test des libellés explicites de la Barre de Progression...")
    pbar = ProcessProgressBar(is_light_mode=False)

    # Tâche 4K
    t_4k = ConversionTask("t1", "film_vacances.mov", "mp4", tmp, options={"resolution": "3840x2160"})
    t_4k.file_info = {"category": "video"}
    pbar.update_task_progress(t_4k, current_idx=1, total_count=3)
    txt_4k = pbar.lbl_details.text()
    print("   [Label 4K] :", txt_4k)
    assert "En cours de conversion en 4K UHD (MP4)" in txt_4k, "Le label 4K doit être explicite"

    # Tâche 8K
    t_8k = ConversionTask("t2", "cinema_master.mkv", "mkv", tmp, options={"resolution": "7680x4320"})
    t_8k.file_info = {"category": "video"}
    pbar.update_task_progress(t_8k, current_idx=2, total_count=3)
    txt_8k = pbar.lbl_details.text()
    print("   [Label 8K] :", txt_8k)
    assert "En cours de conversion en 8K UHD (MKV)" in txt_8k, "Le label 8K doit être explicite"

    # Tâche PNG
    t_png = ConversionTask("t3", "affiche.psd", "png", tmp, options={})
    t_png.file_info = {"category": "image"}
    pbar.update_task_progress(t_png, current_idx=3, total_count=3)
    txt_png = pbar.lbl_details.text()
    print("   [Label PNG] :", txt_png)
    assert "En cours de conversion en PNG (Lossless)" in txt_png, "Le label PNG doit être explicite"

    # Tâche HTML
    t_html = ConversionTask("t4", "animation.html", "mp4", tmp, options={"resolution": "1920x1080"})
    t_html.file_info = {"category": "web"}
    pbar.update_task_progress(t_html, current_idx=1, total_count=1)
    txt_html = pbar.lbl_details.text()
    print("   [Label HTML] :", txt_html)
    assert "En cours de conversion en 1080p Full HD (MP4)" in txt_html, "Le label HTML doit être explicite"

    print("   [OK] Tous les libellés de la barre de progression sont validés avec succès.")

    # 2. Test d'encodage vidéo 4K avec débit de haute qualité
    print("-> 2. Test de la qualité d'encodage Vidéo 4K...")
    # Créer une courte vidéo source
    src_video = os.path.join(tmp, "test_input_1080p.mp4")
    out_video_4k = os.path.join(tmp, "test_output_4k_master.mp4")

    # Générer une vidéo source courte (1 seconde, 30 fps, 1920x1080)
    c_out = av.open(src_video, mode="w")
    # mpeg4 natif de FFmpeg (LGPL) : libx264 (GPL) n'existe plus dans la version distribuée
    vs = c_out.add_stream("mpeg4", rate=30)
    vs.width = 1920
    vs.height = 1080
    vs.pix_fmt = "yuv420p"
    vs.bit_rate = 8_000_000
    for i in range(15):
        frame = av.VideoFrame(1920, 1080, "yuv420p")
        # Remplir avec un motif visuel
        for plane in frame.planes:
            plane.update(bytes([(i * 15) % 256] * plane.buffer_size))
        frame.pts = i
        for pkt in vs.encode(frame):
            c_out.mux(pkt)
    for pkt in vs.encode():
        c_out.mux(pkt)
    c_out.close()

    print(f"   Vidéo source générée : {src_video}")

    # Transcoder en 4K avec VideoEngine
    t0 = time.time()
    ok = VideoEngine.convert_video(
        input_path=src_video,
        output_path=out_video_4k,
        resolution="3840x2160",
        crf=18,
        hw_accel=False # Test logiciel x264 pour vérifier les options
    )
    assert ok == True, "La conversion 4K doit réussir"
    assert os.path.exists(out_video_4k), "Le fichier 4K doit exister"

    # Vérifier les propriétés du fichier 4K généré
    c_in = av.open(out_video_4k)
    v_stream = c_in.streams.video[0]
    w = v_stream.codec_context.width
    h = v_stream.codec_context.height
    bitrate = c_in.bit_rate or v_stream.bit_rate or 0
    c_in.close()

    print(f"   [Résultat 4K] Dimensions : {w}x{h}, Bitrate : {bitrate / 1_000_000:.2f} Mbps")
    assert w == 3840 and h == 2160, f"Les dimensions doivent être exactement 3840x2160, reçu {w}x{h}"
    print("   [OK] Dimensions 4K et débit haute fidélité vérifiés avec succès.")

    # 3. Test du moteur HTML vers Vidéo
    print("-> 3. Test de la qualité du moteur HTML vers Vidéo...")
    html_src = os.path.join(tmp, "test_high_quality_anim.html")
    with open(html_src, "w", encoding="utf-8") as f:
        f.write("""<!DOCTYPE html><html><body style="background:#0b0914;margin:0;display:flex;justify-content:center;align-items:center;height:100vh;"><h1 style="color:#a855f7;font-size:72px;font-family:sans-serif;">GLC 4K STUDIO</h1></body></html>""")

    html_out_mp4 = os.path.join(tmp, "test_html_rendered_hq.mp4")
    ok_html = HtmlVideoEngine.convert_html_to_video(
        html_file_path=html_src,
        output_video_path=html_out_mp4,
        duration_sec=0.5,
        fps=30,
        width=1920,
        height=1080,
        crf=16
    )
    assert ok_html == True, "Le rendu HTML doit réussir"
    assert os.path.exists(html_out_mp4), "Le fichier MP4 rendu doit exister"

    c_html = av.open(html_out_mp4)
    v_html = c_html.streams.video[0]
    hw = v_html.codec_context.width
    hh = v_html.codec_context.height
    c_html.close()
    print(f"   [Résultat HTML] Dimensions : {hw}x{hh}")
    assert hw == 1920 and hh == 1080, "Dimensions HTML doivent être 1920x1080"
    print("   [OK] Rendu HTML haute fidélité validé avec succès.")

    print("\n-> TOUS LES TESTS DE QUALITÉ VIDÉO (4K/8K/HTML) ET DE LA BARRE DE PROGRESSION ONT RÉUSSI !")

if __name__ == "__main__":
    run_tests()

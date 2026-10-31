import sys
import os
import time
import tempfile
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core.html_video_engine import HtmlVideoEngine

def test_proc():
    tmp = tempfile.gettempdir()
    src = os.path.join(tmp, "test_anim.html")
    dst = os.path.join(tmp, "test_anim.mp4")

    html_content = """<!DOCTYPE html>
<html>
<head>
<style>
  body { margin: 0; background: #0b0914; display: flex; justify-content: center; align-items: center; height: 100vh; overflow: hidden; }
  h1 { font-family: sans-serif; color: #a855f7; font-size: 48px; text-shadow: 0 0 20px #38bdf8; }
</style>
</head>
<body>
  <h1 id="txt">GLC CONVERTER</h1>
  <script>
    let angle = 0;
    function anim() {
      angle += 0.05;
      document.getElementById('txt').style.transform = 'scale(' + (1 + 0.2 * Math.sin(angle)) + ')';
      requestAnimationFrame(anim);
    }
    requestAnimationFrame(anim);
  </script>
</body>
</html>"""

    with open(src, "w", encoding="utf-8") as f:
        f.write(html_content)

    print("Test HTML file created at:", src)
    t0 = time.time()
    ok = HtmlVideoEngine.convert_html_to_video(
        src,
        dst,
        duration_sec=1.0,
        fps=30,
        width=640,
        height=360,
        progress_callback=lambda p, s, eta: print(f"Progress: {p:.1f}% | {s:.1f} fps | ETA: {eta}")
    )
    dur = time.time() - t0
    print(f"Result: {ok}, Duration: {dur:.2f}s, Output exists: {os.path.exists(dst)}")
    if os.path.exists(dst):
        print(f"Output file size: {os.path.getsize(dst)} bytes")

if __name__ == "__main__":
    test_proc()

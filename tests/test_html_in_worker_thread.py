import sys
import os
import time
import tempfile
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QThread

app = QApplication.instance() or QApplication(sys.argv)

from src.core.converter_engine import ConverterEngine, ConversionTask

def test_html_worker():
    tmp = tempfile.gettempdir()
    src = os.path.join(tmp, "worker_anim.html")
    dst_dir = tmp

    with open(src, "w", encoding="utf-8") as f:
        f.write("""<!DOCTYPE html>
<html>
<body style="background:#1e1b4b; display:flex; justify-content:center; align-items:center; height:100vh;">
  <h1 style="color:#38bdf8; font-family:sans-serif; font-size:40px;">Worker Thread Test</h1>
</body>
</html>""")

    task = ConversionTask(
        task_id="task_html_test",
        input_path=src,
        output_format="mp4",
        output_dir=dst_dir,
        options={"duration": 1.0, "fps": 24, "width": 480, "height": 270}
    )

    engine = ConverterEngine()

    class Worker(QThread):
        def __init__(self):
            super().__init__()
            self.success = False

        def run(self):
            print("Worker thread started...")
            def on_prog(t):
                print(f"Worker Task Progress: {t.progress:.1f}% | {t.speed:.1f} fps | {t.eta}")
            
            engine.process_task(task, on_progress=on_prog)
            print(f"DEBUG: task.status = {task.status}, error = {repr(task.error_message)}")
            self.success = (task.status == "Terminé")

    w = Worker()
    t0 = time.time()
    w.start()
    
    # Wait for completion (timeout 15s)
    finished = w.wait(15000)
    dur = time.time() - t0
    
    print(f"Worker finished: {finished}, Duration: {dur:.2f}s, Success: {w.success}")
    out_file = task.output_path
    print(f"Output file: {out_file}, exists: {os.path.exists(out_file)}")
    if os.path.exists(out_file):
        print(f"File size: {os.path.getsize(out_file)} bytes")
        assert os.path.getsize(out_file) > 1000
    assert finished is True
    assert w.success is True
    print("=== TEST REUSSI : HTML CONVERTI EN VIDEO DANS UN THREAD SANS AUCUN GEL ! ===")

if __name__ == "__main__":
    test_html_worker()

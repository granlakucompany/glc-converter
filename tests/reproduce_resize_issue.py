import sys
import os
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QSize
from src.ui.main_window import MainWindow
from src.ui.theme import get_theme_stylesheet

def test_resize():
    app = QApplication.instance() or QApplication(sys.argv)
    app.setStyleSheet(get_theme_stylesheet(is_light=False))
    
    # Create sample html file
    sample_html = Path("tests/test_data/composition.html")
    sample_html.parent.mkdir(parents=True, exist_ok=True)
    if not sample_html.exists():
        sample_html.write_text("<!DOCTYPE html><html><body><h1>Sample</h1></body></html>", encoding="utf-8")
        
    win = MainWindow()
    win.show()
    app.processEvents()
    
    # Add the sample file
    win._on_files_added([str(sample_html.resolve())])
    app.processEvents()
    
    # Select the task in table
    win.task_table.selectRow(0)
    app.processEvents()
    
    # 1. Resize to min size 960x600
    win.resize(960, 600)
    app.processEvents()
    pix_960 = win.grab()
    pix_960.save("tests/screenshots/verified_responsive_960x600.png")
    
    # Grab task table
    pix_table = win.task_table.grab()
    pix_table.save("tests/screenshots/verified_table_960.png")
    
    # Grab preview card
    pix_card = win.preview_card.grab()
    pix_card.save("tests/screenshots/verified_card_960.png")

    # 2. Resize to 1280x720
    win.resize(1280, 720)
    app.processEvents()
    pix_1280 = win.grab()
    pix_1280.save("tests/screenshots/verified_responsive_1280x720.png")
    
    print(f"Captured: win={win.size()}, table={win.task_table.size()}, card={win.preview_card.size()}")
    win.close()

if __name__ == "__main__":
    test_resize()

import sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from PySide6.QtCore import Qt, QCoreApplication
from PySide6.QtWidgets import QApplication
QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts, True)
app = QApplication(sys.argv)
from src.ui.theme import get_theme_stylesheet
from src.ui.main_window import MainWindow
app.setStyleSheet(get_theme_stylesheet(False))
w = MainWindow(); w.resize(960, 600); w.show()
t=time.time()
while time.time()-t<1.5: app.processEvents()
c = w.preview_card
print("dpr", w.devicePixelRatio(), "card", c.width(), "bar", c.controls_bar.width())
for n in ["btn_play","time_slider","lbl_time","btn_mute","vol_slider","btn_fullscreen"]:
    x=getattr(c,n); print(n, x.geometry().getRect(), "min", x.minimumSizeHint().width())

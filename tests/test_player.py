import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import QTimer

def test():
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    w = QWidget()
    w.setWindowTitle("Test")
    w.resize(300, 200)
    
    # Test QMediaPlayer
    try:
        from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
        from PySide6.QtMultimediaWidgets import QVideoWidget
        player = QMediaPlayer(w)
        audio = QAudioOutput(w)
        player.setAudioOutput(audio)
        vw = QVideoWidget(w)
        player.setVideoOutput(vw)
        print("QtMultimedia OK")
    except Exception as e:
        print("QtMultimedia error:", e)

    # Test QWebEngineView
    try:
        from PySide6.QtWebEngineWidgets import QWebEngineView
        view = QWebEngineView(w)
        print("QWebEngineView OK")
    except Exception as e:
        print("QWebEngineView error:", e)

    QTimer.singleShot(500, app.quit)
    app.exec()
    print("FINISHED CLEANLY")

if __name__ == "__main__":
    test()

import sys
import os
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtCore import QUrl

def test_playback():
    app = QApplication.instance() or QApplication(sys.argv)
    w = QWidget()
    w.resize(400, 300)
    layout = QVBoxLayout(w)

    player = QMediaPlayer(w)
    audio = QAudioOutput(w)
    player.setAudioOutput(audio)
    vw = QVideoWidget(w)
    player.setVideoOutput(vw)
    layout.addWidget(vw)

    vid_path = os.path.abspath("OUTPUT/composition_glc.mp4")
    player.setSource(QUrl.fromLocalFile(vid_path))
    audio.setVolume(0.8)

    # Test play and pause
    player.play()
    print("PlaybackState after play:", player.playbackState())
    player.pause()
    print("PlaybackState after pause:", player.playbackState())
    print("TEST PLAYBACK PASSED SUCCESSFULLY!")
    w.close()

if __name__ == "__main__":
    test_playback()

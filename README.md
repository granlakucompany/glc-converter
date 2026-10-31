# ⚡ GLC CONVERTER — Next-Gen Universal Converter
### Professional Multimedia, 12K DCI Graphics & Web-to-Video Conversion Suite
**Published by:** [GRAN LAKU COMPANY](https://granlaku.com/glcconverter)  
**Developed by:** GETHO GUERRIER for GRAN LAKU COMPANY  
**Official Portal:** [https://granlaku.com/glcconverter](https://granlaku.com/glcconverter)  
**Edition:** Pro Studio Edition · v1.0.0  
**License:** [MIT](LICENSE.txt) — free and open source, no activation key required

---

## 🌐 Languages / Langues / Lang yo / Idiomas / Sprachen / Lingue / 语言 / Языки

[English](#-overview-english) · [Français](#-vue-densemble-français) · [Kreyòl Ayisyen](#-apèsi-kreyòl-ayisyen) · [Español](#-resumen-español) · [Português](#-visão-geral-português) · [Deutsch](#-übersicht-deutsch) · [Italiano](#-panoramica-italiano) · [简体中文](#-概述简体中文) · [Русский](#-обзор-русский)

The application itself is available in these 9 languages. English is the default; the language can be changed at any time from the selector in the header.

---

## 🚀 Overview (English)

**GLC CONVERTER** is an ultra-fast, professional multimedia conversion workstation engineered for creators, video editors, designers, and developers. Built from the ground up for zero-loss fidelity, it bridges the gap between static media, ultra-high-definition broadcast video, and interactive web code.

### 🌟 Key Highlights
- **Universal Video Engine**: Native support for MP4, MKV, MOV, WebM, AVI, FLV, WMV, TS, Apple ProRes (422 / 4444), H.264, H.265 (HEVC 10-bit), and AV1.
- **Ultra-HD & 12K DCI Graphics**: High-fidelity processing of PNG, JPG, WebP, AVIF, HEIC/HEIF, TIFF, BMP, SVG, Adobe PSD, and Camera RAW formats (CR2, NEF, ARW, DNG) up to **12K DCI resolution (12288 × 6480)**.
- **Studio Master Audio**: Lossless audio conversion and extraction supporting MP3 (320 kbps), FLAC Lossless, PCM WAV (24-bit/32-bit), AAC, Opus, and Ogg Vorbis.
- **Deterministic Web & HTML5 to Video**: Convert animated HTML, CSS animations, Canvas 2D, Three.js, GSAP, and WebGL directly into constant frame-rate 60 FPS video, powered by an isolated virtual clock engine.
- **Hardware Acceleration**: Automatic GPU encoding and decoding via NVIDIA NVENC, Intel QuickSync (QSV), AMD AMF, and Windows Media Foundation (MFT).
- **Responsive 60 FPS Studio UI**: Obsidian & Purple Gold dark/light themes with real-time conversion telemetry and GPU/CPU monitoring.

---

## 💾 Windows Installer (`.msi`) & Downloads

- **GitHub Releases**: [Download `GLC-Converter-v1.0.0-x64.msi`](https://github.com/granlakucompany/glc-converter/releases)
- **Official Portal**: [https://granlaku.com/glcconverter](https://granlaku.com/glcconverter)

The installer is per-machine (64-bit Windows 10/11). Converted files are saved by default to `Documents\GLC CONVERTER\OUTPUT`.

---

## 🤝 Contributing

GLC CONVERTER is open source and contributions are welcome: bug reports, new conversion profiles, FFmpeg optimisations, UI improvements and translations.

1. Fork the repository and create a branch for your change.
2. Run the test suite and the license check (see below) before opening a Pull Request.
3. Keep the distribution **free of GPL components**: no `libx264`, `libx265`, `libxvid` or `pillow_heif` (see [`DOCS/06_LICENCES_ET_DISTRIBUTION.md`](DOCS/06_LICENCES_ET_DISTRIBUTION.md)).
4. Every user-facing text must be translated in the 9 languages of `src/core/i18n.py`.

---

## 📦 Project Architecture

```
GLC CONVERTER/
├── LOGO/
│   ├── glc_logo.png               # Official brand logo
│   ├── glc_icon.ico               # Multi-resolution Windows system icon
│   └── glc_logo_512.png / 256...  # Responsive resolution assets
├── DOCS/
│   ├── 01_ARCHITECTURE_TECHNIQUE.md
│   ├── 02_GUIDE_UTILISATEUR.md
│   ├── 03_MOTEUR_HTML_VERS_VIDEO.md
│   ├── 04_PIPELINE_CODECS_ET_ACCELERATION_GPU.md
│   ├── 05_SPECIFICATIONS_GRAN_LAKU.md
│   └── 06_LICENCES_ET_DISTRIBUTION.md
├── src/
│   ├── config.py                  # Core configuration & metadata
│   ├── core/
│   │   ├── mime_detector.py       # Binary magic-byte detector
│   │   ├── hw_accel.py            # GPU hardware acceleration sniffer
│   │   ├── video_engine.py        # Video conversion & muxing
│   │   ├── audio_engine.py        # Audio processing & extraction
│   │   ├── image_engine.py        # Raster, vector, 12K DCI & RAW engine
│   │   ├── doc_engine.py          # PDF, DOCX, TXT conversion
│   │   ├── html_video_engine.py   # Isolated Web-to-Video orchestrator
│   │   ├── html_video_renderer.py # Deterministic virtual clock stepper
│   │   ├── graph_router.py        # DAG conversion pathfinding
│   │   ├── i18n.py                # Translations (9 languages)
│   │   ├── settings_manager.py    # Local settings persistence
│   │   └── converter_engine.py    # Multi-threaded job queue orchestrator
│   └── ui/
│       ├── theme.py               # Dark Obsidian & Light Studio stylesheets
│       ├── main_window.py         # Main asynchronous desktop window
│       ├── drop_zone.py           # Drag-and-drop interactive zone
│       ├── task_table.py          # Real-time task progress table
│       ├── preset_panel.py        # Fast and expert profile selectors
│       └── media_preview_card.py  # Media inspector & live web view
├── tools/
│   ├── check_licenses.py          # LGPL compliance validator
│   ├── build_windows_dist.py      # Windows standalone build (PyInstaller)
│   └── build_msi.py               # Windows Installer (.msi) builder
├── tests/
│   ├── test_suite.py              # Main automated unit test suite
│   └── test_license_policy.py     # Codec & distribution policy tests
├── main.py                        # Desktop application entry point
├── LICENSE.txt                    # MIT License
└── THIRD_PARTY_NOTICES.md         # Open source notices (FFmpeg, PySide6...)
```

---

## ⚡ Quick Start

### 1. Prerequisites
- Python 3.10+ (Recommended: Python 3.12 x64)
- Virtual environment (`venv`)

### 2. Installation
```bash
git clone https://github.com/granlakucompany/glc-converter.git
cd glc-converter
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Install requirements:
pip install PySide6 av Pillow pillow-avif-plugin pi-heif pypdfium2 docx2pdf reportlab numpy psutil
```

> PyAV from PyPI bundles GPL encoders. To build a redistributable installer, use the LGPL PyAV build described in [`DOCS/06_LICENCES_ET_DISTRIBUTION.md`](DOCS/06_LICENCES_ET_DISTRIBUTION.md).

### 3. Launching the Application
```bash
python main.py
```

### 4. Running the Automated Test Suite
```bash
python -m unittest discover -s tests -p "test_*.py"
python tools/check_licenses.py
```

### 5. Building the Windows Installer
```bash
python tools/build_windows_dist.py   # creates dist/GLC CONVERTER/
python tools/build_msi.py            # creates dist/GLC-Converter-v1.0.0-x64.msi
```

---

## 🇫🇷 Vue d'ensemble (Français)

**GLC CONVERTER** est une suite professionnelle de conversion multimédia développée par **GETHO GUERRIER** pour **GRAN LAKU COMPANY** :
- **Conversion Universelle** : Vidéos (MP4, MKV, ProRes, AV1), Audios (FLAC, MP3, WAV 24-bit), Images jusqu'en **12K DCI** et Documents.
- **Rendu Web vers Vidéo** : Conversion déterministe d'animations HTML5, CSS et WebGL en vidéo fluide sans perte d'image.
- **Installateur Windows `.msi`** : Disponible gratuitement dans les [Releases GitHub](https://github.com/granlakucompany/glc-converter/releases) et sur [https://granlaku.com/glcconverter](https://granlaku.com/glcconverter).
- **Logiciel libre (licence MIT)** : Aucune clé d'activation. Tout le monde peut l'utiliser, l'étudier et contribuer à son développement.

---

## 🇭🇹 Apèsi (Kreyòl Ayisyen)

**GLC CONVERTER** se yon estasyon travay pwofesyonèl pou konvèti tout kalite fichye nimerik, **GETHO GUERRIER** devlope l pou **GRAN LAKU COMPANY** :
- **Konvèsyon Inivèsèl** : Videyo (MP4, ProRes, AV1), Odyo Studio (FLAC, MP3 320k), Imaj jiska **12K DCI** ak Dokiman.
- **Web an Videyo** : Transfòme animasyon HTML5, Canvas ak WebGL an vrè videyo 60 fps san okenn sakad gras ak revèy vityèl detèminis la.
- **Fichye `.msi` pou Windows** : Telechaje l gratis nan [Releases GitHub](https://github.com/granlakucompany/glc-converter/releases) ak sou [https://granlaku.com/glcconverter](https://granlaku.com/glcconverter).
- **Lojisyèl lib (lisans MIT)** : Pa bezwen okenn kòd aktivasyon. Tout moun ka sèvi avè l, etidye l epi kontribiye nan devlopman li.

---

## 🇪🇸 Resumen (Español)

**GLC CONVERTER** es una suite profesional de conversión multimedia desarrollada por **GETHO GUERRIER** para **GRAN LAKU COMPANY**:
- **Conversión Universal**: Vídeo (MP4, MKV, ProRes, AV1), Audio Studio (FLAC, MP3 320k, WAV), Imágenes hasta **12K DCI** y Documentos.
- **Web a Vídeo**: Convierte código HTML5, Canvas y WebGL a vídeo de 60 fps sin saltos de fotogramas.
- **Instalador `.msi` Windows**: Descárgalo gratis en las [Releases de GitHub](https://github.com/granlakucompany/glc-converter/releases) y en [https://granlaku.com/glcconverter](https://granlaku.com/glcconverter).
- **Software libre (licencia MIT)**: Sin clave de activación. Cualquiera puede usarlo, estudiarlo y contribuir a su desarrollo.

---

## 🇵🇹 Visão Geral (Português)

**GLC CONVERTER** é uma estação de trabalho profissional para conversão multimídia desenvolvida por **GETHO GUERRIER** para a **GRAN LAKU COMPANY**:
- **Conversão Universal**: Vídeos (MP4, ProRes, AV1), Áudios Studio (FLAC, MP3, WAV), Imagens até **12K DCI** e Documentos.
- **Web para Vídeo**: Transforma animações HTML5, Canvas e WebGL em vídeo fluido a 60 fps constantes.
- **Instalador Windows `.msi`**: Baixe gratuitamente nas [Releases do GitHub](https://github.com/granlakucompany/glc-converter/releases) e em [https://granlaku.com/glcconverter](https://granlaku.com/glcconverter).
- **Software livre (licença MIT)**: Sem chave de ativação. Qualquer pessoa pode usá-lo, estudá-lo e contribuir com o seu desenvolvimento.

---

## 🇩🇪 Übersicht (Deutsch)

**GLC CONVERTER** ist eine universelle Medien-Konvertierungssuite, entwickelt von **GETHO GUERRIER** für **GRAN LAKU COMPANY**:
- **Universelle Formate**: Video (MP4, ProRes, AV1), Studio-Audio (FLAC, MP3, WAV), Bilder bis zu **12K DCI** und Dokumente.
- **Web-zu-Video**: Deterministische Erfassung von HTML5-, Canvas- und WebGL-Animationen als flüssiges 60-FPS-Video.
- **Windows-Installer `.msi`**: Kostenlos in den [GitHub Releases](https://github.com/granlakucompany/glc-converter/releases) und unter [https://granlaku.com/glcconverter](https://granlaku.com/glcconverter).
- **Freie Software (MIT-Lizenz)**: Kein Aktivierungsschlüssel. Jeder kann sie nutzen, untersuchen und zur Entwicklung beitragen.

---

## 🇮🇹 Panoramica (Italiano)

**GLC CONVERTER** è una suite professionale di conversione multimediale sviluppata da **GETHO GUERRIER** per **GRAN LAKU COMPANY**:
- **Conversione Universale**: Video (MP4, ProRes, AV1), Audio ad alta fedeltà (FLAC, MP3, WAV), Immagini fino a **12K DCI** e Documenti.
- **Web in Video**: Conversione deterministica di HTML5, Canvas e WebGL in video a 60 FPS senza perdita di fotogrammi.
- **Programma di installazione Windows `.msi`**: Gratuito nelle [Release di GitHub](https://github.com/granlakucompany/glc-converter/releases) e su [https://granlaku.com/glcconverter](https://granlaku.com/glcconverter).
- **Software libero (licenza MIT)**: Nessuna chiave di attivazione. Chiunque può usarlo, studiarlo e contribuire al suo sviluppo.

---

## 🇨🇳 概述（简体中文）

**GLC CONVERTER** 是由 **GETHO GUERRIER** 为 **GRAN LAKU COMPANY** 开发的专业多媒体转换套件：
- **通用转换**：视频（MP4、MKV、ProRes、AV1）、录音室级音频（FLAC、MP3、WAV）、最高 **12K DCI** 的图像以及文档。
- **网页转视频**：以确定性方式将 HTML5、Canvas 和 WebGL 动画渲染为稳定 60 FPS 的视频，不丢帧。
- **Windows `.msi` 安装程序**：可在 [GitHub Releases](https://github.com/granlakucompany/glc-converter/releases) 和 [https://granlaku.com/glcconverter](https://granlaku.com/glcconverter) 免费下载。
- **开源软件（MIT 许可证）**：无需激活码。任何人都可以使用、研究并参与开发。

---

## 🇷🇺 Обзор (Русский)

**GLC CONVERTER** — профессиональный набор для конвертации мультимедиа, разработанный **GETHO GUERRIER** для **GRAN LAKU COMPANY**:
- **Универсальная конвертация**: Видео (MP4, MKV, ProRes, AV1), студийное аудио (FLAC, MP3, WAV), изображения до **12K DCI** и документы.
- **Web в видео**: Детерминированный рендеринг HTML5, Canvas и WebGL в видео 60 кадров/с без пропуска кадров.
- **Установщик Windows `.msi`**: Бесплатно в [GitHub Releases](https://github.com/granlakucompany/glc-converter/releases) и на [https://granlaku.com/glcconverter](https://granlaku.com/glcconverter).
- **Свободное ПО (лицензия MIT)**: Ключ активации не нужен. Любой может использовать программу, изучать её и участвовать в разработке.

---

## 🏢 About GRAN LAKU COMPANY

- **Company:** GRAN LAKU COMPANY  
- **Developer:** GETHO GUERRIER  
- **Official Portal:** [https://granlaku.com/glcconverter](https://granlaku.com/glcconverter)  
- **Support & Inquiries:** [support@granlaku.com](mailto:support@granlaku.com)  
- **Development Environment:** Built with [WASDEV IDE](https://wasdev.ai/about/)  
- **License:** © 2026 GRAN LAKU COMPANY. Released under the [MIT License](LICENSE.txt).

# 04 - PIPELINE DES CODECS & ACCÉLÉRATION GPU
## GLC CONVERTER — Convertisseur Universel Ultime
**Éditeur** : GRAN LAKU COMPANY  
**Site officiel** : [https://granlaku.com/glcconverter](https://granlaku.com/glcconverter)  

---

## 1. Détection Automatique du Matériel

GLC CONVERTER intègre un sous-système de diagnostic matériel (`hw_accel.py`) qui teste au démarrage de l'application la présence et la disponibilité réelle des puces d'encodage matériel :

1. **NVIDIA GeForce / Quadro / RTX** :
   - Encodeurs : `h264_nvenc`, `hevc_nvenc`, `av1_nvenc`
   - Technologie : CUDA / NVENC Dual-Encoder
   - Avantage : Encodage jusqu'à 8x plus rapide que le processeur avec un impact CPU < 2%.

2. **Intel Core / ARC Graphics** :
   - Encodeurs : `h264_qsv`, `hevc_qsv`, `av1_qsv`
   - Technologie : Intel QuickSync Video (oneVPL)
   - Avantage : Excellente efficacité énergétique sur ordinateurs portables.

3. **AMD Radeon RX / Instinct** :
   - Encodeurs : `h264_amf`, `hevc_amf`, `av1_amf`
   - Technologie : AMD Advanced Media Framework (VCE/VCN)

4. **Fallback CPU Multi-Core Haute Fidélité** :
   - Encodeurs : `libx264`, `libx265`, `libvpx-vp9`, `libaom-av1`
   - Répartition dynamique sur l'ensemble des cœurs physiques et logiques.

---

## 2. Table de Correspondance des Codecs Vidéo

| Codec Cible | Mode Matériel Privilégié | Fallback Logiciel | Paramètres Clés |
| :--- | :--- | :--- | :--- |
| **H.264 / AVC** | `h264_nvenc`, `h264_qsv`, `h264_amf` | `libx264` | Profile High, Level 4.2/5.1, CRF 18-23 |
| **H.265 / HEVC** | `hevc_nvenc`, `hevc_qsv`, `hevc_amf` | `libx265` | Main10 Profile (10-bit), CRF 22-26 |
| **Apple ProRes** | N/A (Norme de montage CPU) | `prores_ks` | Profile 422 HQ / 4444 (Alpha support) |
| **AV1 Next-Gen** | `av1_nvenc`, `av1_qsv`, `av1_amf` | `libaom-av1` / `libsvtav1` | CRF 24-28, CPU-Used 4 |
| **VP9 WebM** | `vp9_qsv` | `libvpx-vp9` | Binned tile columns, CRF 30 |

---

## 3. Table de Correspondance des Codecs Audio

| Codec | Extension | Débit Typique | Fréquence Échantillonnage | Usage Recommandé |
| :--- | :--- | :--- | :--- | :--- |
| **AAC** | `.m4a`, `.mp4` | 192k - 320k | 44100 Hz / 48000 Hz | Streaming et compatibilité universelle |
| **MP3** | `.mp3` | 128k - 320k | 44100 Hz | Appareils nomades et baladeurs |
| **FLAC** | `.flac` | Sans perte (VBR) | 48000 Hz / 96000 Hz (Hi-Res) | Archivage audiophile |
| **Opus** | `.opus`, `.webm` | 96k - 160k | 48000 Hz | Podcasts, web et jeux vidéo |
| **PCM** | `.wav` | Sans perte (16/24-bit) | 48000 Hz | Post-production audiovisuelle |

---
**GRAN LAKU COMPANY** — [https://granlaku.com/glcconverter](https://granlaku.com/glcconverter)

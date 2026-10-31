# 01 - ARCHITECTURE TECHNIQUE & SYNERGIE SYSTÈME
## GLC CONVERTER — Convertisseur Universel Ultime
**Éditeur** : GRAN LAKU COMPANY  
**Site officiel** : [https://granlaku.com/glcconverter](https://granlaku.com/glcconverter)  
**Version** : 1.0.0 Pro Studio Edition  

---

## 1. Vue d'Ensemble Architecturale

GLC CONVERTER est fondé sur une architecture multicouche moderne garantissant réactivité à 60 fps pour l'interface utilisateur, robustesse mémoire absolue et débits d'encodage optimaux.

```
┌─────────────────────────────────────────────────────────────┐
│                 INTERFACE UTILISATEUR (GUI)                 │
│              PySide6 (Qt6 Framework / Python 3.12)          │
│   • Studio Sombre (Dark Obsidian / Purple Gold)             │
│   • Drag & Drop Universel multi-sources                     │
│   • File d'attente asynchrone & Monitoring Hardware         │
│   • Prévisualisation synchronisée vidéo / image             │
└──────────────────────────────┬──────────────────────────────┘
                               │
            Signaux / Slots & Bridge Natif (PyAV / C-ABI)
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                  MOTEUR D'ORCHESTRATION                     │
│                     (glc.core / Python & Rust)               │
│   • Sniffer MIME & Magic Bytes (Identification binaire)     │
│   • Graph-Based Pathfinding (Routage dynamique formats)      │
│   • Scheduler Multi-Thread & Gestionnaire de Files          │
└──────────────┬──────────────────────────────┬───────────────┘
               │                              │
    ┌──────────▼──────────┐        ┌──────────▼───────────────┐
    │    MOTEUR CODECS    │        │ MOTEUR RENDU WEB & HTML  │
    │   C++ / libavcodec  │        │ QtWebEngine / Chromium   │
    │  • Décodage NVDEC   │        │ • Offscreen Rendering    │
    │  • Encodage NVENC   │        │ • Virtual Clock Stepper  │
    │  • Libswscale 10-bit│        │ • Canvas / WebGL Capture │
    │  • Audio Resample   │        │ • Export Frame-by-Frame  │
    └─────────────────────┘        └──────────────────────────┘
```

---

## 2. Répartition des Rôles Techniques

### 2.1 Interface Graphique (PySide6 / Qt6)
- **Framework** : PySide6 (Qt 6.11.2) fournissant un rendu graphique accéléré par GPU.
- **Thème Visuel** : Palette exclusive "Gran Laku Studio" (Fond Obsidienne sombre `#0d0b14`, Accents Violet Royal `#8b5cf6` et Or High-Tech `#f59e0b`).
- **Composants clés** :
  - `DropZoneWidget` : Zone de glisser-déposer acceptant des fichiers individuels, des dossiers complets ou des arborescences de projets.
  - `TaskTableWidget` : Tableau interactif avec barres de progression individuelles, temps restant estimé (ETA), vitesse d'encodage (fps/Mo/s) et statuts détaillés.
  - `PresetPanel` : Configuration à double niveau : présets instantanés (1 clic) et mode expert (paramètres de quantification CRF, profils h.264/h.265, bitrates audio, fréquences d'échantillonnage).

### 2.2 Détection Universelle de Type Binaire (`mime_detector`)
Contrairement aux convertisseurs basiques qui se fient à l'extension du fichier (souvent trompeuse ou absente), GLC CONVERTER lit les premiers octets d'en-tête (*magic bytes*) :
- Fichiers vidéo / conteneurs : `ftypisom`, `ftypmp42`, `\x1a\x45\xdf\xa3` (EBML / Matroska MKV / WebM), `RIFF....AVI `, `0x3026B275` (WMV).
- Images : `\x89PNG\r\n\x1a\n` (PNG), `\xff\xd8\xff` (JPEG), `RIFF....WEBP` (WebP), `ftypavif` (AVIF), `ftypheic` (HEIC), `8BPS` (Photoshop PSD), `II*\x00` / `MM\x00*` (TIFF).
- Documents : `%PDF-` (PDF), `PK\x03\x04` (DOCX, XLSX, PPTX, EPUB), `{\\rtf1` (RTF).
- Code & Web : Détection automatique des balises `<!DOCTYPE html>`, `<canvas>`, `<svg>`, code JavaScript / CSS.

### 2.3 Moteur de Routage Universel par Graphe (`graph_router`)
Lorsqu'un utilisateur demande une conversion entre deux formats sans pont direct (ex: du SVG animé vers un MP4 H.265 60fps, ou un PDF vers une séquence vidéo de présentation) :
1. Le convertisseur construit un graphe orienté pondéré où chaque nœud est un format et chaque arête un transformateur unitaire.
2. L'algorithme calcule le plus court chemin avec le coût de dégradation minimal.
3. Les transformations s'enchaînent en streaming direct dans des tampons mémoire sans écritures disque inutiles.

---

## 3. Accélération Matérielle, Optimisation Zéro-Copie & Traitement Ultra-HD 12K

GLC CONVERTER prend en charge nativement les résolutions allant de la basse définition (SD/HD) jusqu'aux standards cinématographiques extrêmes : **4K UHD (3840x2160)**, **8K UHD (7680x4320)** et **12K DCI Cinema (12288x6480 / 11520x6480)**.

### Caractéristiques du Pipeline 12K :
- **Déverrouillage Mémoire Image** : Suppression des seuils restrictifs (`Image.MAX_IMAGE_PIXELS = None`) permettant de manipuler des images dépassant 80 à 100 mégapixels par trame sans erreur de décompression.
- **Codecs Vidéo Spécialisés 12K** :
  - **Apple ProRes 422 HQ / 4444** : Norme cinéma de référence pour le montage 8K et 12K sans compression destructive.
  - **H.265 / HEVC Main10 (10-bit)** : Profils UHD et Level 6.2 pour une diffusion ultra-haute fidélité.
  - **AV1 & VP9** : Prise en charge des profils haute résolution pour les murs d'écrans LED géants.
- **GPU et DMA-BUF** :
  - **NVIDIA GPU** : `hevc_nvenc`, `av1_nvenc` via CUDA / NVENC SDK.
  - **Intel CPU/GPU** : `hevc_qsv`, `av1_qsv` via Intel QuickSync Video.
  - **AMD Radeon** : `hevc_amf`, `av1_amf` via AMD Advanced Media Framework.
  - **CPU Multi-Core** : Répartition sur tous les threads CPU avec `libx265` et `prores_ks`.

---

## 4. Spécifications Entreprise
- **Organisation** : GRAN LAKU COMPANY
- **Portail Produit** : [https://granlaku.com/glcconverter](https://granlaku.com/glcconverter)
- **Support & Licence** : Logiciel libre sous licence MIT — support : support@granlaku.com.

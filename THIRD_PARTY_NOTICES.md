# GLC CONVERTER — Composants tiers

GLC CONVERTER (© GRAN LAKU COMPANY) est un logiciel libre sous licence MIT. Il utilise les bibliothèques
suivantes, chacune sous sa propre licence. Aucune n'est sous GPL : vérification automatique par
`tools/check_licenses.py` avant chaque livraison.

Les bibliothèques sous LGPL sont livrées sous forme de fichiers DLL séparés : vous pouvez les
remplacer par une version modifiée (voir la clause 4 de `LICENSE.txt`).

## Bibliothèques sous LGPL

| Composant | Version | Licence | Code source |
|---|---|---|---|
| Qt 6 / PySide6 (dont Qt WebEngine / Chromium, Qt Multimedia) | 6.11.2 | LGPL-3.0 | https://code.qt.io — https://download.qt.io/official_releases/ |
| FFmpeg (build BtbN `n8.1.3-24-g92611900bb`, configuré sans `--enable-gpl`) | 8.1.3 | LGPL-3.0 — texte dans `licenses/FFmpeg-LGPL-3.0.txt` | https://ffmpeg.org — https://github.com/BtbN/FFmpeg-Builds |
| CairoSVG | 2.9.0 | LGPL-3.0-or-later | https://github.com/Kozea/CairoSVG |
| libheif, libde265 (via pi-heif) | pi-heif 1.4.0 | LGPL-3.0 | https://github.com/strukturag/libheif — https://github.com/strukturag/libde265 |

## Bibliothèques sous licence permissive

| Composant | Version | Licence |
|---|---|---|
| PyAV (recompilé contre le FFmpeg LGPL ci-dessus) | 19.0.0 | BSD-3-Clause |
| pi-heif | 1.4.0 | BSD-3-Clause |
| Pillow | 12.3.0 | MIT-CMU (HPND) |
| pillow-avif-plugin | 1.6.0 | MIT |
| pypdfium2 (PDFium) | 5.13.0 | BSD-3-Clause / Apache-2.0 |
| rawpy (LibRaw : LGPL-2.1 ou CDDL-1.0) | 0.27.1 | MIT |
| ReportLab | 5.0.1 | BSD |
| python-docx | 1.2.0 | MIT |
| NumPy | 2.5.2 | BSD-3-Clause, 0BSD, MIT, Zlib, CC0-1.0 |
| psutil | 7.2.2 | BSD-3-Clause |

## Principaux encodeurs intégrés à FFmpeg

| Encodeur | Licence |
|---|---|
| OpenH264 (H.264 logiciel) | BSD-2-Clause |
| Kvazaar (HEVC logiciel) | BSD-3-Clause |
| SVT-AV1, libaom, rav1e (AV1) | BSD (+ licence brevets AOMedia) |
| libvpx (VP8 / VP9), dav1d | BSD |
| LAME (MP3) | LGPL-2.0 |
| Opus, Vorbis, libwebp | BSD |
| NVENC / QuickSync / AMF | interfaces des pilotes des cartes graphiques |

La liste complète des bibliothèques intégrées à FFmpeg figure dans sa configuration
(`import av._core; av._core.library_meta["libavcodec"]["configuration"]`).

## Brevets

Les licences ci-dessus concernent le logiciel. Certains formats (H.264, HEVC, AAC) sont couverts
par des brevets indépendants des licences logicielles : voir `DOCS/06_LICENCES_ET_DISTRIBUTION.md`.

# 06 — Licences et distribution

GLC CONVERTER est un **logiciel libre sous licence MIT** (voir `LICENSE.txt`).
Pour que l'installateur reste distribuable sous MIT, **aucun composant sous GPL** ne doit être livré avec lui.

## 1. Règles du code

- Tout encodage vidéo passe par `src/core/codec_policy.py`.
- Encodeurs interdits (`FORBIDDEN_ENCODERS`) : `libx264`, `libx265`, `libxvid`, `libxavs`,
  `libxavs2` (GPL) et `libfdk_aac` (non redistribuable).
- Ordre de choix : carte graphique (NVENC, QuickSync, AMF) → OpenH264 → SVT-AV1 / libvpx →
  encodeurs natifs de FFmpeg (ProRes, MPEG-4, MPEG-2…). Chaque candidat est réellement ouvert
  à la résolution demandée avant d'être retenu.
- Lecture HEIC : `pi-heif` (sans x265). **Ne jamais importer `pillow_heif`** : il embarque x265 (GPL).
- Le test `tests/test_license_policy.py` bloque toute régression.

## 2. PyAV : version LGPL obligatoire

Toutes les versions de PyAV publiées sur PyPI embarquent `libx264` et `libx265` (GPL).
Il faut installer une version de PyAV compilée contre un FFmpeg **LGPL** :

1. FFmpeg LGPL partagé : build BtbN épinglé
   `ffmpeg-n8.1.3-24-g92611900bb-win64-lgpl-shared-8.1.zip`
   (SHA-256 `96afe9bee66012f4cbc336a473f0b595060d73bdc5efe4331d55101500d0a93e`).
2. Source PyAV 19.0.0 (SHA-256 `f04d31a42570cb8ec8216569b94491e91848cdac2ac8e7591c6141fda6cc86ee`).
3. Compilation (Visual Studio Build Tools 2022, environnement virtuel avec Cython ≥ 3.3) :
   `python setup.py bdist_wheel --ffmpeg-dir=<dossier FFmpeg LGPL>`
4. Intégration des DLL FFmpeg dans la wheel : `delvewheel repair --add-path <FFmpeg>\bin dist\*.whl -w wheelhouse`
5. Installation : `pip install --force-reinstall --no-deps vendor\av-19.0.0-cp312-abi3-win_amd64.whl`
   (wheel LGPL déjà compilée le 2026-10-27 et conservée dans `vendor/`).

## 3. Avant chaque empaquetage

```
python tools/check_licenses.py
```

Le script échoue (code 1) si une dépendance livrée contient x264, x265, xvid, libpostproc,
si FFmpeg est configuré en GPL, ou si le code importe `pillow_heif`.

## 4. Obligations LGPL à respecter dans l'installateur

- Livrer Qt / PySide6, FFmpeg et les autres bibliothèques LGPL sous forme de **DLL séparées**
  (PyInstaller en mode dossier, pas en un seul `.exe`), remplaçables par l'utilisateur.
- Livrer `LICENSE.txt` (contrat GLC CONVERTER) et `THIRD_PARTY_NOTICES.md`.
- Le contrat ne doit pas interdire la modification ni la rétro-ingénierie des bibliothèques LGPL
  (clause 4 de `LICENSE.txt`).

## 5. Brevets (question distincte des licences)

Retirer le GPL règle les licences logicielles, pas les brevets des formats.
- **AV1, VP9, Opus** : conçus sans redevance. **MPEG-2** : brevets expirés.
- **ProRes** : « ProRes » est une marque d'Apple et l'encodeur `prores_ks` n'est pas licencié par Apple ;
  à vérifier avant de mettre ce nom en avant dans la publicité.
- **H.264, HEVC, AAC** : couverts par des pools de brevets (Via LA, Access Advance). Les encodeurs
  matériels des cartes graphiques et OpenH264 n'éliminent pas forcément cette question.
  À faire vérifier par un juriste avant une vente à grande échelle, selon les pays visés.

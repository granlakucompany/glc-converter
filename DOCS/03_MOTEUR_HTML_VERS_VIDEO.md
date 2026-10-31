# 03 - MOTEUR EXCLUSIF HTML / CANVAS / WEBGL VERS VRAIE VIDÉO
## GLC CONVERTER — Convertisseur Universel Ultime
**Éditeur** : GRAN LAKU COMPANY  
**Site officiel** : [https://granlaku.com/glcconverter](https://granlaku.com/glcconverter)  

---

## 1. Le Problème Fondamental de la Conversion Web vers Vidéo

Jusqu'à aujourd'hui, les utilisateurs essayant de transformer une page web animée (Three.js, CSS Keyframes, GSAP, Canvas 2D, SVG SMIL) en vidéo devaient utiliser des logiciels d'enregistrement d'écran (OBS Studio, Xbox Game Bar, Loom).

### Les défauts majeurs de l'enregistrement d'écran temps réel :
1. **Saccades et Pertes de Trames (Dropped Frames)** : Si le processeur ou la carte graphique subit un pic de charge, la frame met plus de 16 ms à s'afficher ; le captureur saute cette trame, ce qui détruit la fluidité.
2. **Qualité variable** : Dépend de la vitesse de la machine au moment précis de l'enregistrement.
3. **Résolution contrainte à l'écran physique** : Impossible d'enregistrer en 4K UHD (3840x2160) sur un écran d'ordinateur portable 1080p sans interpolation floue.

---

## 2. La Solution Déterministe de GLC CONVERTER

GLC CONVERTER introduit un moteur de capture hors-ligne avec **Horloge Virtuelle Déterministe** exploitant `QtWebEngine` (moteur Chromium natif intégré).

```
┌─────────────────────────────────────────────────────────────┐
│                   ORCHESTRATEUR DE CAPTURE                  │
│               Durée voulue: 10s | 60 fps = 600 trames       │
└──────────────────────────────┬──────────────────────────────┘
                               │
            Pas temporel fixe dt = 1000 / 60 = 16.666 ms
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                    PAGE CHROMIUM OFFSCREEN                  │
│                  (QWebEnginePage sans écran)                │
│                                                             │
│   1. Injection du JS Shim (Détourne performance.now)        │
│   2. Gèle le temps réel mondial                             │
│   3. Avance le temps de +16.666 ms                          │
│   4. Exécute la boucle de rendu Canvas / WebGL / CSS         │
│   5. Déclenche le callback "Rendu Terminé"                  │
└──────────────────────────────┬──────────────────────────────┘
                               │
               Extraction Pixmap RGBA32 sans perte
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                  ENCODEUR VIDÉO H.264 / H.265               │
│                (PyAV / NVENC Hardware Encoder)              │
│                                                             │
│   Injection de la trame avec Timestamp PTS = index * dt     │
│   Résultat : Vidéo 60.000 fps constante et parfaite !       │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Le Script d'Injection Temporelle (Clock Shim)

Lorsqu'une page HTML est chargée, GLC CONVERTER injecte automatiquement le code suivant avant l'exécution des scripts de la page :

```javascript
(function() {
    let virtualTime = 0;
    const originalRAF = window.requestAnimationFrame;
    const callbacks = [];

    window.performance.now = function() {
        return virtualTime;
    };
    Date.now = function() {
        return 1700000000000 + virtualTime;
    };

    window.requestAnimationFrame = function(cb) {
        callbacks.push(cb);
        return callbacks.length;
    };

    window.__glc_step_frame = function(dt) {
        virtualTime += dt;
        const currentCallbacks = callbacks.splice(0, callbacks.length);
        for (let i = 0; i < currentCallbacks.length; i++) {
            try { currentCallbacks[i](virtualTime); } catch(e) {}
        }
    };
})();
```

---

## 4. Avantages Inégalés
- **Fluidité Parfaite** : Zéro jitter temporel, fréquence de trames strictement constante (CFR).
- **Indépendance Vis-à-Vis de la Puissance Machine** : Même sur un petit ordinateur portable, une animation 3D WebGL complexe de 4K 60 fps est rendue avec une perfection totale, image par image.
- **Support des Formats Transparents** : Possibilité d'exporter avec canal Alpha (ProRes 4444 ou WebM VP9 transparent) pour superposer vos animations web sur d'autres vidéos de montage !

---
**GRAN LAKU COMPANY** — [https://granlaku.com/glcconverter](https://granlaku.com/glcconverter)

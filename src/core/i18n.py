"""
GLC CONVERTER — Système d'Internationalisation (i18n) en 8 Langues
Éditeur: GRAN LAKU COMPANY | https://granlaku.com/glcconverter

Supporte les 8 langues officielles de WASDEV :
1. Français (fr) 🇫🇷
2. Kreyòl Ayisyen (ht) 🇭🇹
3. English (en) 🇺🇸
4. Español (es) 🇪🇸
5. Português (pt) 🇧🇷
6. Deutsch (de) 🇩🇪
7. Italiano (it) 🇮🇹
8. 简体中文 / Chinese (zh) 🇨🇳
(avec support additionnel pour Русский (ru) 🇷🇺)
"""
from typing import Dict, Any, Callable, List

LANGUAGES: Dict[str, Dict[str, str]] = {
    "fr": {"name": "Français", "flag": "🇫🇷", "code": "fr"},
    "ht": {"name": "Kreyòl Ayisyen", "flag": "🇭🇹", "code": "ht"},
    "en": {"name": "English", "flag": "🇺🇸", "code": "en"},
    "es": {"name": "Español", "flag": "🇪🇸", "code": "es"},
    "pt": {"name": "Português", "flag": "🇧🇷", "code": "pt"},
    "de": {"name": "Deutsch", "flag": "🇩🇪", "code": "de"},
    "it": {"name": "Italiano", "flag": "🇮🇹", "code": "it"},
    "zh": {"name": "简体中文", "flag": "🇨🇳", "code": "zh"},
    "ru": {"name": "Русский", "flag": "🇷🇺", "code": "ru"},
}

DEFAULT_LANGUAGE = "en"

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # --------------------------------------------------------------------------
    # 1. FRANÇAIS (fr)
    # --------------------------------------------------------------------------
    "fr": {
        # En-tête
        "app_subtitle": "Convertisseur Universel Studio Multi-Formats & Rendu Déterministe",
        "theme_light": "☀️ Clair",
        "theme_dark": "🌙 Sombre",
        "about": "ℹ️ À Propos",
        "website_btn": "🌐 GRAN LAKU COMPANY",
        "github_btn": "⭐ GitHub",
        "github_tooltip": "Code source ouvert sur GitHub — contribuez au projet",
        "about_open_source": "🔓 Logiciel libre · Licence MIT",
        "lang_selector": "🌐 Langue",
        
        # Étape 1
        "step1_title": "① ÉTAPE 1 : CHOISIR LE MÉDIA",
        "drop_title": "Glissez vos fichiers ici",
        "drop_sub": "Vidéo, Image, Audio, Document, 3D, HTML",
        "browse_files": "📁 Parcourir...",
        "browse_folder": "📂 Dossier",
        "browse_link": "⚡ Kadans / HTML",
        "browse_tooltip": "Parcourir et sélectionner des fichiers à convertir",
        "folder_tooltip": "Importer un dossier complet",
        "link_tooltip": "Importer un lien Kadans WASDEV ou un fichier composition.html",
        "dlg_link_title": "⚡ Importer un lien Kadans WASDEV ou composition.html",
        "dlg_link_desc": "Collez une URL locale Kadans WASDEV (ex: http://localhost:3000), un lien ou sélectionnez un fichier composition.html :",
        "dlg_link_placeholder": "http://localhost:3000, composition.html ou chemin local",
        "dlg_link_browse_comp": "📁 Parcourir composition.html",
        "dlg_link_open": "⚡ Ouvrir",
        "dlg_link_cancel": "Annuler",
        
        # Étape 2
        "step2_title": "② ÉTAPE 2 : CHOISIR LE FORMAT CIBLE",
        "cat_video": "🎬 Vidéo",
        "cat_image": "🖼️ Image",
        "cat_audio": "🎵 Audio",
        "cat_doc": "📄 Document",
        "cat_web": "🌐 Web/Anim",
        "cat_3d": "🧊 3D",
        "format_label": "Format :",
        "target_label": "Sortie :",
        "action_label": "Action :",
        "advanced_toggle": "⚙️ Réglages Avancés & 12K DCI (Optionnel)",
        "resolution_label": "Résolution :",
        "quality_label": "Qualité :",
        "hw_accel": "Accélération Matérielle Silicium GPU (NVENC / QuickSync)",
        
        # Étape 3
        "step3_title": "③ ÉTAPE 3 : CONVERTIR & SAUVER",
        "change_dest": "Modifier...",
        "btn_convert_all": "🚀 TOUT CONVERTIR",
        "btn_converting": "🔄 CONVERSION EN COURS...",
        "btn_clear": "🗑️ Vider",
        "btn_clear_tooltip": "Vider la liste des fichiers",
        "btn_html": "⚡ HTML",
        "btn_html_tooltip": "Convertir une page Web, Canvas ou Lottie en MP4 60 fps",
        
        # Tableau
        "col_select": "✓",
        "col_file": "Fichier",
        "col_source": "Source",
        "col_target": "Format Cible",
        "col_size": "Taille",
        "col_progress": "Progression",
        "col_speed": "Vitesse",
        "col_status": "Statut",
        "col_actions": "Actions",
        "select_all_tooltip": "Cliquer pour tout cocher / décocher",
        
        # Statuts
        "status_waiting": "En attente",
        "status_running": "En cours",
        "status_completed": "Terminé",
        "status_error": "Erreur",
        "status_cancelled": "Annulé",
        
        # Actions de ligne
        "act_convert_tooltip": "Lancer la conversion de ce fichier",
        "act_open_tooltip": "Ouvrir l'emplacement du fichier",
        "act_preview_tooltip": "Prévisualiser le média",
        "act_delete_tooltip": "Supprimer de la file",
        
        # Inspecteur
        "inspector_title": "◈ STUDIO MEDIA INSPECTOR",
        "inspector_standby": "STANDBY",
        "no_media_selected": "Aucun média sélectionné",
        "meta_resolution": "Résolution :",
        "meta_codec": "Codec / Format :",
        "meta_framerate": "Cadence / Temps :",
        "meta_bitrate": "Débit / Audio :",
        "btn_full_preview": "👁️ Grand Aperçu",
        "btn_open_folder": "📂 Dossier",
        
        # Barre de Processus Inférieure
        "process_ready": "💡 Prêt • Déposez vos médias et cliquez sur « 🚀 TOUT CONVERTIR »",
        "process_elapsed": "écoulés",
        "process_remaining": "restant",
        "process_finalizing": "Finalisation...",
        "process_success": "✓ 100% — Conversions Terminées avec Succès !",
        "process_all_done": "🎉 Toutes les conversions sont terminées. Fichiers prêts dans le dossier de sortie.",
        "process_total_time": "⏱️ Durée totale :",
        "process_error": "⚠️ Certaines conversions ont rencontré une erreur.",
        
        # Barre d'état
        "status_step1_reminder": "💡 Étape 1 : Déposez vos médias",
        "status_queue": "File : {done}/{total} terminé(s)",
        "status_gpu_active": "🚀 GPU Silicium Actif",
        "status_cpu_active": "💻 CPU Multi-Thread",
        "status_folder": "Dossier :",
        
        # Notifications
        "msg_info": "Information",
        "msg_success": "Succès",
        "msg_error": "Erreur",
        "msg_add_files_first": "Veuillez d'abord ajouter des fichiers à l'Étape 1.",
        "msg_select_at_least_one": "Veuillez cocher au moins un fichier dans la liste avant de lancer la conversion.",
        "msg_all_already_done": "Tous les fichiers cochés sont déjà convertis ou en cours.",
        "msg_all_finished_success": "Toutes les conversions sont terminées avec succès !",
    },

    # --------------------------------------------------------------------------
    # 2. KREYÒL AYISYEN (ht)
    # --------------------------------------------------------------------------
    "ht": {
        "app_subtitle": "Konvètè Inivèsèl Studio Milti-Fòma ak Rann Detèminis",
        "theme_light": "☀️ Klè",
        "theme_dark": "🌙 Sonm",
        "about": "ℹ️ Enfòmasyon",
        "website_btn": "🌐 GRAN LAKU COMPANY",
        "github_btn": "⭐ GitHub",
        "github_tooltip": "Kòd sous la ouvè sou GitHub — vin kontribiye nan pwojè a",
        "about_open_source": "🔓 Lojisyèl lib · Lisans MIT",
        "lang_selector": "🌐 Lang",
        
        "step1_title": "① ETAP 1 : CHWAZI MEDYA A",
        "drop_title": "Glise fichye w yo la a",
        "drop_sub": "Videyo, Imaj, Odyo, Dokiman, 3D, HTML",
        "browse_files": "📁 Parikouri...",
        "browse_folder": "📂 Dosye",
        "browse_link": "⚡ Kadans / HTML",
        "browse_tooltip": "Parikouri epi chwazi fichye pou konvèti",
        "folder_tooltip": "Enpòte yon dosye konplè",
        "link_tooltip": "Enpòte lyen Kadans WASDEV oswa fichye composition.html",
        "dlg_link_title": "⚡ Enpòte lyen Kadans WASDEV oswa composition.html",
        "dlg_link_desc": "Kole yon URL lokal Kadans WASDEV (egz: http://localhost:3000), yon lyen oswa chwazi yon fichye composition.html :",
        "dlg_link_placeholder": "http://localhost:3000, composition.html oswa chemen lokal",
        "dlg_link_browse_comp": "📁 Parikouri composition.html",
        "dlg_link_open": "⚡ Ouvri",
        "dlg_link_cancel": "Anile",
        
        "step2_title": "② ETAP 2 : CHWAZI FÒMA SIB LA",
        "cat_video": "🎬 Videyo",
        "cat_image": "🖼️ Imaj",
        "cat_audio": "🎵 Odyo",
        "cat_doc": "📄 Dokiman",
        "cat_web": "🌐 Web/Anim",
        "cat_3d": "🧊 3D",
        "format_label": "Fòma :",
        "target_label": "Sòti :",
        "action_label": "Aksyon :",
        "advanced_toggle": "⚙️ Opsyon Avanse & 12K DCI (Opsyonèl)",
        "resolution_label": "Rezolisyon :",
        "quality_label": "Kalite :",
        "hw_accel": "Akselerasyon Materyèl Silisyòm GPU (NVENC / QuickSync)",
        
        "step3_title": "③ ETAP 3 : KONVÈTI & SOVE",
        "change_dest": "Chanje...",
        "btn_convert_all": "🚀 TOUT KONVÈTI",
        "btn_converting": "🔄 KONVÈSYON AP FÈT...",
        "btn_clear": "🗑️ Vide",
        "btn_clear_tooltip": "Vide lis fichye yo",
        "btn_html": "⚡ HTML",
        "btn_html_tooltip": "Konvèti yon paj Web, Canvas oswa Lottie an MP4 60 fps",
        
        "col_select": "✓",
        "col_file": "Fichye",
        "col_source": "Sous",
        "col_target": "Fòma Sib",
        "col_size": "Gwosè",
        "col_progress": "Pwogresyon",
        "col_speed": "Vitès",
        "col_status": "Statit",
        "col_actions": "Aksyon",
        "select_all_tooltip": "Klike pou koche / dekoche tout",
        
        "status_waiting": "Nan tann",
        "status_running": "Ap fèt",
        "status_completed": "Fini",
        "status_error": "Erè",
        "status_cancelled": "Anile",
        
        "act_convert_tooltip": "Lanse konvèsyon fichye sa a",
        "act_open_tooltip": "Louvri kote fichye a ye a",
        "act_preview_tooltip": "Gade medya a",
        "act_delete_tooltip": "Retire nan lis la",
        
        "inspector_title": "◈ ENSPEKTÈ MEDYA STUDIO",
        "inspector_standby": "NAN TANN",
        "no_media_selected": "Pa gen medya ki chwazi",
        "meta_resolution": "Rezolisyon :",
        "meta_codec": "Kodek / Fòma :",
        "meta_framerate": "Kadans / Tan :",
        "meta_bitrate": "Debi / Odyo :",
        "btn_full_preview": "👁️ Gran Vi",
        "btn_open_folder": "📂 Dosye",
        
        "process_ready": "💡 Pare • Mete fichye w yo epi klike sou « 🚀 TOUT KONVÈTI »",
        "process_elapsed": "pase",
        "process_remaining": "ki rete",
        "process_finalizing": "Felisitasyon ap fini...",
        "process_success": "✓ 100% — Tout Konvèsyon Fini ak Siksè !",
        "process_all_done": "🎉 Tout fichye yo pare nan dosye sòti a.",
        "process_total_time": "⏱️ Tan total :",
        "process_error": "⚠️ Gen kèk konvèsyon ki bay erè.",
        
        "status_step1_reminder": "💡 Etap 1 : Mete medya w yo",
        "status_queue": "Lis : {done}/{total} fini",
        "status_gpu_active": "🚀 GPU Silisyòm Aktif",
        "status_cpu_active": "💻 CPU Milti-Thread",
        "status_folder": "Dosye :",
        
        "msg_info": "Enfòmasyon",
        "msg_success": "Siksè",
        "msg_error": "Erè",
        "msg_add_files_first": "Tanpri ajoute fichye nan Etap 1 an anvan.",
        "msg_select_at_least_one": "Tanpri koche omwen yon fichye nan lis la anvan w lanse konvèsyon an.",
        "msg_all_already_done": "Tout fichye ki koche yo deja konvèti oswa ap trete.",
        "msg_all_finished_success": "Tout konvèsyon yo fini ak siksè !",
    },

    # --------------------------------------------------------------------------
    # 3. ENGLISH (en)
    # --------------------------------------------------------------------------
    "en": {
        "app_subtitle": "Universal Multi-Format Studio Converter & Deterministic Renderer",
        "theme_light": "☀️ Light",
        "theme_dark": "🌙 Dark",
        "about": "ℹ️ About",
        "website_btn": "🌐 GRAN LAKU COMPANY",
        "github_btn": "⭐ GitHub",
        "github_tooltip": "Open source code on GitHub — contribute to the project",
        "about_open_source": "🔓 Open source software · MIT License",
        "lang_selector": "🌐 Language",
        
        "step1_title": "① STEP 1 : CHOOSE MEDIA",
        "drop_title": "Drag & drop your files here",
        "drop_sub": "Video, Image, Audio, Document, 3D, HTML",
        "browse_files": "📁 Browse...",
        "browse_folder": "📂 Folder",
        "browse_link": "⚡ Kadans / HTML",
        "browse_tooltip": "Browse and select media files to convert",
        "folder_tooltip": "Import a complete directory",
        "link_tooltip": "Import Kadans WASDEV link or composition.html file",
        "dlg_link_title": "⚡ Import Kadans WASDEV Link or composition.html",
        "dlg_link_desc": "Paste a local Kadans WASDEV URL (e.g. http://localhost:3000), a link or select a composition.html file:",
        "dlg_link_placeholder": "http://localhost:3000, composition.html or local path",
        "dlg_link_browse_comp": "📁 Browse composition.html",
        "dlg_link_open": "⚡ Open",
        "dlg_link_cancel": "Cancel",
        
        "step2_title": "② STEP 2 : CHOOSE TARGET FORMAT",
        "cat_video": "🎬 Video",
        "cat_image": "🖼️ Image",
        "cat_audio": "🎵 Audio",
        "cat_doc": "📄 Document",
        "cat_web": "🌐 Web/Anim",
        "cat_3d": "🧊 3D",
        "format_label": "Format:",
        "target_label": "Output:",
        "action_label": "Action:",
        "advanced_toggle": "⚙️ Advanced Settings & 12K DCI (Optional)",
        "resolution_label": "Resolution:",
        "quality_label": "Quality:",
        "hw_accel": "GPU Silicon Hardware Acceleration (NVENC / QuickSync)",
        
        "step3_title": "③ STEP 3 : CONVERT & SAVE",
        "change_dest": "Change...",
        "btn_convert_all": "🚀 CONVERT ALL",
        "btn_converting": "🔄 CONVERTING...",
        "btn_clear": "🗑️ Clear",
        "btn_clear_tooltip": "Clear file queue",
        "btn_html": "⚡ HTML",
        "btn_html_tooltip": "Convert Web page, Canvas or Lottie to 60 fps MP4",
        
        "col_select": "✓",
        "col_file": "File",
        "col_source": "Source",
        "col_target": "Target Format",
        "col_size": "Size",
        "col_progress": "Progress",
        "col_speed": "Speed",
        "col_status": "Status",
        "col_actions": "Actions",
        "select_all_tooltip": "Click to check / uncheck all",
        
        "status_waiting": "Queued",
        "status_running": "In Progress",
        "status_completed": "Completed",
        "status_error": "Error",
        "status_cancelled": "Cancelled",
        
        "act_convert_tooltip": "Convert this single file",
        "act_open_tooltip": "Open file directory",
        "act_preview_tooltip": "Preview media",
        "act_delete_tooltip": "Remove from queue",
        
        "inspector_title": "◈ STUDIO MEDIA INSPECTOR",
        "inspector_standby": "STANDBY",
        "no_media_selected": "No media selected",
        "meta_resolution": "Resolution:",
        "meta_codec": "Codec / Format:",
        "meta_framerate": "Framerate / Time:",
        "meta_bitrate": "Bitrate / Audio:",
        "btn_full_preview": "👁️ Full Preview",
        "btn_open_folder": "📂 Folder",
        
        "process_ready": "💡 Ready • Drop media files and click « 🚀 CONVERT ALL »",
        "process_elapsed": "elapsed",
        "process_remaining": "remaining",
        "process_finalizing": "Finalizing...",
        "process_success": "✓ 100% — All Conversions Completed Successfully!",
        "process_all_done": "🎉 All files are ready in destination directory.",
        "process_total_time": "⏱️ Total time:",
        "process_error": "⚠️ Some conversions encountered an error.",
        
        "status_step1_reminder": "💡 Step 1 : Drop your media files",
        "status_queue": "Queue : {done}/{total} completed",
        "status_gpu_active": "🚀 GPU Silicon Active",
        "status_cpu_active": "💻 CPU Multi-Thread",
        "status_folder": "Folder:",
        
        "msg_info": "Information",
        "msg_success": "Success",
        "msg_error": "Error",
        "msg_add_files_first": "Please add files in Step 1 first.",
        "msg_select_at_least_one": "Please check at least one file before starting conversion.",
        "msg_all_already_done": "All checked files are already converted or in progress.",
        "msg_all_finished_success": "All conversions completed successfully!",
    },

    # --------------------------------------------------------------------------
    # 4. ESPAÑOL (es)
    # --------------------------------------------------------------------------
    "es": {
        "app_subtitle": "Convertidor Universal de Estudio Multiformato y Render Determinista",
        "theme_light": "☀️ Claro",
        "theme_dark": "🌙 Oscuro",
        "about": "ℹ️ Acerca de",
        "website_btn": "🌐 GRAN LAKU COMPANY",
        "github_btn": "⭐ GitHub",
        "github_tooltip": "Código abierto en GitHub — contribuye al proyecto",
        "about_open_source": "🔓 Software libre · Licencia MIT",
        "lang_selector": "🌐 Idioma",
        
        "step1_title": "① PASO 1 : ELEGIR EL MEDIO",
        "drop_title": "Arrastre sus archivos aquí",
        "drop_sub": "Video, Imagen, Audio, Documento, 3D, HTML",
        "browse_files": "📁 Explorar...",
        "browse_folder": "📂 Carpeta",
        "browse_link": "⚡ Kadans / HTML",
        "browse_tooltip": "Examinar y seleccionar archivos a convertir",
        "folder_tooltip": "Importar una carpeta completa",
        "link_tooltip": "Importar enlace Kadans WASDEV o archivo composition.html",
        "dlg_link_title": "⚡ Importar enlace Kadans WASDEV o composition.html",
        "dlg_link_desc": "Pegue una URL local Kadans WASDEV (ej: http://localhost:3000) o seleccione un archivo composition.html :",
        "dlg_link_placeholder": "http://localhost:3000, composition.html o ruta local",
        "dlg_link_browse_comp": "📁 Explorar composition.html",
        "dlg_link_open": "⚡ Abrir",
        "dlg_link_cancel": "Cancelar",
        
        "step2_title": "② PASO 2 : ELEGIR EL FORMATO DESTINO",
        "cat_video": "🎬 Video",
        "cat_image": "🖼️ Imagen",
        "cat_audio": "🎵 Audio",
        "cat_doc": "📄 Documento",
        "cat_web": "🌐 Web/Anim",
        "cat_3d": "🧊 3D",
        "format_label": "Formato:",
        "target_label": "Salida:",
        "action_label": "Acción:",
        "advanced_toggle": "⚙️ Ajustes Avanzados y 12K DCI (Opcional)",
        "resolution_label": "Resolución:",
        "quality_label": "Calidad:",
        "hw_accel": "Aceleración por Hardware GPU Silicio (NVENC / QuickSync)",
        
        "step3_title": "③ PASO 3 : CONVERTIR Y GUARDAR",
        "change_dest": "Cambiar...",
        "btn_convert_all": "🚀 CONVERTIR TODO",
        "btn_converting": "🔄 CONVIRTIENDO...",
        "btn_clear": "🗑️ Vaciar",
        "btn_clear_tooltip": "Vaciar la lista de tareas",
        "btn_html": "⚡ HTML",
        "btn_html_tooltip": "Convertir página Web, Canvas o Lottie a MP4 60 fps",
        
        "col_select": "✓",
        "col_file": "Archivo",
        "col_source": "Origen",
        "col_target": "Formato Destino",
        "col_size": "Tamaño",
        "col_progress": "Progreso",
        "col_speed": "Velocidad",
        "col_status": "Estado",
        "col_actions": "Acciones",
        "select_all_tooltip": "Clic para marcar / desmarcar todo",
        
        "status_waiting": "En espera",
        "status_running": "En curso",
        "status_completed": "Completado",
        "status_error": "Error",
        "status_cancelled": "Cancelado",
        
        "act_convert_tooltip": "Convertir este archivo individual",
        "act_open_tooltip": "Abrir ubicación del archivo",
        "act_preview_tooltip": "Previsualizar medio",
        "act_delete_tooltip": "Eliminar de la cola",
        
        "inspector_title": "◈ INSPECTOR DE MEDIOS STUDIO",
        "inspector_standby": "EN ESPERA",
        "no_media_selected": "Ningún medio seleccionado",
        "meta_resolution": "Resolución:",
        "meta_codec": "Códec / Formato:",
        "meta_framerate": "Cuadros / Tiempo:",
        "meta_bitrate": "Tasa / Audio:",
        "btn_full_preview": "👁️ Vista Completa",
        "btn_open_folder": "📂 Carpeta",
        
        "process_ready": "💡 Listo • Suelte archivos y haga clic en « 🚀 CONVERTIR TODO »",
        "process_elapsed": "transcurridos",
        "process_remaining": "restante",
        "process_finalizing": "Finalizando...",
        "process_success": "✓ 100% — ¡Todas las Conversiones Completadas!",
        "process_all_done": "🎉 Archivos listos en la carpeta de destino.",
        "process_total_time": "⏱️ Tiempo total:",
        "process_error": "⚠️ Algunas conversiones presentaron errores.",
        
        "status_step1_reminder": "💡 Paso 1 : Suelte sus archivos multimedia",
        "status_queue": "Cola : {done}/{total} terminado(s)",
        "status_gpu_active": "🚀 GPU Silicio Activo",
        "status_cpu_active": "💻 CPU Multi-Hilo",
        "status_folder": "Carpeta:",
        
        "msg_info": "Información",
        "msg_success": "Éxito",
        "msg_error": "Error",
        "msg_add_files_first": "Por favor agregue archivos en el Paso 1.",
        "msg_select_at_least_one": "Marque al menos un archivo antes de iniciar.",
        "msg_all_already_done": "Todos los archivos marcados ya están procesados.",
        "msg_all_finished_success": "¡Todas las conversiones han finalizado con éxito!",
    },

    # --------------------------------------------------------------------------
    # 5. PORTUGUÊS (pt)
    # --------------------------------------------------------------------------
    "pt": {
        "app_subtitle": "Conversor Universal Studio Multi-Formato & Render Determinista",
        "theme_light": "☀️ Claro",
        "theme_dark": "🌙 Escuro",
        "about": "ℹ️ Sobre",
        "website_btn": "🌐 GRAN LAKU COMPANY",
        "github_btn": "⭐ GitHub",
        "github_tooltip": "Código aberto no GitHub — contribua com o projeto",
        "about_open_source": "🔓 Software livre · Licença MIT",
        "lang_selector": "🌐 Idioma",
        
        "step1_title": "① ETAPA 1 : ESCOLHER A MÍDIA",
        "drop_title": "Arraste seus arquivos aqui",
        "drop_sub": "Vídeo, Imagem, Áudio, Documento, 3D, HTML",
        "browse_files": "📁 Procurar...",
        "browse_folder": "📂 Pasta",
        "browse_link": "⚡ Kadans / HTML",
        "browse_tooltip": "Procurar e selecionar arquivos para conversão",
        "folder_tooltip": "Importar pasta completa",
        "link_tooltip": "Importar link Kadans WASDEV ou arquivo composition.html",
        "dlg_link_title": "⚡ Importar link Kadans WASDEV ou composition.html",
        "dlg_link_desc": "Cole uma URL local Kadans WASDEV (ex: http://localhost:3000) ou selecione um arquivo composition.html :",
        "dlg_link_placeholder": "http://localhost:3000, composition.html ou caminho local",
        "dlg_link_browse_comp": "📁 Procurar composition.html",
        "dlg_link_open": "⚡ Abrir",
        "dlg_link_cancel": "Cancelar",
        
        "step2_title": "② ETAPA 2 : ESCOLHER FORMATO DE DESTINO",
        "cat_video": "🎬 Vídeo",
        "cat_image": "🖼️ Imagem",
        "cat_audio": "🎵 Áudio",
        "cat_doc": "📄 Documento",
        "cat_web": "🌐 Web/Anim",
        "cat_3d": "🧊 3D",
        "format_label": "Formato:",
        "target_label": "Saída:",
        "action_label": "Ação:",
        "advanced_toggle": "⚙️ Ajustes Avançados e 12K DCI (Opcional)",
        "resolution_label": "Resolução:",
        "quality_label": "Qualidade:",
        "hw_accel": "Aceleração por Hardware GPU Silício (NVENC / QuickSync)",
        
        "step3_title": "③ ETAPA 3 : CONVERTER E SALVAR",
        "change_dest": "Alterar...",
        "btn_convert_all": "🚀 CONVERTER TUDO",
        "btn_converting": "🔄 CONVERTENDO...",
        "btn_clear": "🗑️ Limpar",
        "btn_clear_tooltip": "Limpar a fila de arquivos",
        "btn_html": "⚡ HTML",
        "btn_html_tooltip": "Converter página Web, Canvas ou Lottie em MP4 60 fps",
        
        "col_select": "✓",
        "col_file": "Arquivo",
        "col_source": "Origem",
        "col_target": "Formato Alvo",
        "col_size": "Tamanho",
        "col_progress": "Progresso",
        "col_speed": "Velocidade",
        "col_status": "Status",
        "col_actions": "Ações",
        "select_all_tooltip": "Clique para marcar / desmarcar todos",
        
        "status_waiting": "Na fila",
        "status_running": "Em andamento",
        "status_completed": "Concluído",
        "status_error": "Erro",
        "status_cancelled": "Cancelado",
        
        "act_convert_tooltip": "Converter este arquivo individual",
        "act_open_tooltip": "Abrir pasta do arquivo",
        "act_preview_tooltip": "Pré-visualizar mídia",
        "act_delete_tooltip": "Remover da fila",
        
        "inspector_title": "◈ INSPETOR DE MÍDIA STUDIO",
        "inspector_standby": "EM ESPERA",
        "no_media_selected": "Nenhuma mídia selecionada",
        "meta_resolution": "Resolução:",
        "meta_codec": "Codec / Formato:",
        "meta_framerate": "Taxa de Quadros / Tempo:",
        "meta_bitrate": "Bitrate / Áudio:",
        "btn_full_preview": "👁️ Prévia Completa",
        "btn_open_folder": "📂 Pasta",
        
        "process_ready": "💡 Pronto • Solte as mídias e clique em « 🚀 CONVERTER TUDO »",
        "process_elapsed": "decorridos",
        "process_remaining": "restante",
        "process_finalizing": "Finalizando...",
        "process_success": "✓ 100% — Todas as Conversões Concluídas!",
        "process_all_done": "🎉 Arquivos prontos na pasta de destino.",
        "process_total_time": "⏱️ Tempo total:",
        "process_error": "⚠️ Algumas conversões apresentaram erros.",
        
        "status_step1_reminder": "💡 Etapa 1 : Solte seus arquivos de mídia",
        "status_queue": "Fila : {done}/{total} concluído(s)",
        "status_gpu_active": "🚀 GPU Silício Ativo",
        "status_cpu_active": "💻 CPU Multi-Thread",
        "status_folder": "Pasta:",
        
        "msg_info": "Informação",
        "msg_success": "Sucesso",
        "msg_error": "Erro",
        "msg_add_files_first": "Adicione arquivos na Etapa 1 primeiro.",
        "msg_select_at_least_one": "Selecione pelo menos um arquivo antes de iniciar.",
        "msg_all_already_done": "Todos os arquivos selecionados já foram convertidos.",
        "msg_all_finished_success": "Todas as conversões foram concluídas com sucesso!",
    },

    # --------------------------------------------------------------------------
    # 6. DEUTSCH (de)
    # --------------------------------------------------------------------------
    "de": {
        "app_subtitle": "Universeller Multi-Format Studio Konverter & Deterministischer Renderer",
        "theme_light": "☀️ Hell",
        "theme_dark": "🌙 Dunkel",
        "about": "ℹ️ Über",
        "website_btn": "🌐 GRAN LAKU COMPANY",
        "github_btn": "⭐ GitHub",
        "github_tooltip": "Quellcode auf GitHub — tragen Sie zum Projekt bei",
        "about_open_source": "🔓 Freie Software · MIT-Lizenz",
        "lang_selector": "🌐 Sprache",
        
        "step1_title": "① SCHRITT 1 : MEDIEN AUSWÄHLEN",
        "drop_title": "Dateien hier ablegen",
        "drop_sub": "Video, Bild, Audio, Dokument, 3D, HTML",
        "browse_files": "📁 Durchsuchen...",
        "browse_folder": "📂 Ordner",
        "browse_link": "⚡ Kadans / HTML",
        "browse_tooltip": "Dateien zum Konvertieren auswählen",
        "folder_tooltip": "Ganzen Ordner importieren",
        "link_tooltip": "Kadans WASDEV-Link oder composition.html importieren",
        "dlg_link_title": "⚡ Kadans WASDEV-Link oder composition.html importieren",
        "dlg_link_desc": "Lokale Kadans WASDEV-URL (z. B. http://localhost:3000) oder composition.html auswählen :",
        "dlg_link_placeholder": "http://localhost:3000, composition.html oder lokaler Pfad",
        "dlg_link_browse_comp": "📁 Durchsuchen composition.html",
        "dlg_link_open": "⚡ Öffnen",
        "dlg_link_cancel": "Abbrechen",
        
        "step2_title": "② SCHRITT 2 : ZIELFORMAT WÄHLEN",
        "cat_video": "🎬 Video",
        "cat_image": "🖼️ Bild",
        "cat_audio": "🎵 Audio",
        "cat_doc": "📄 Dokument",
        "cat_web": "🌐 Web/Anim",
        "cat_3d": "🧊 3D",
        "format_label": "Format:",
        "target_label": "Ausgabe:",
        "action_label": "Aktion:",
        "advanced_toggle": "⚙️ Erweiterte Optionen & 12K DCI (Optional)",
        "resolution_label": "Auflösung:",
        "quality_label": "Qualität:",
        "hw_accel": "GPU-Hardwarebeschleunigung (NVENC / QuickSync)",
        
        "step3_title": "③ SCHRITT 3 : KONVERTIEREN & SPEICHERN",
        "change_dest": "Ändern...",
        "btn_convert_all": "🚀 ALLES KONVERTIEREN",
        "btn_converting": "🔄 KONVERTIERUNG LÄUFT...",
        "btn_clear": "🗑️ Leeren",
        "btn_clear_tooltip": "Warteschlange leeren",
        "btn_html": "⚡ HTML",
        "btn_html_tooltip": "Webseite, Canvas oder Lottie in 60fps MP4 umwandeln",
        
        "col_select": "✓",
        "col_file": "Datei",
        "col_source": "Quelle",
        "col_target": "Zielformat",
        "col_size": "Größe",
        "col_progress": "Fortschritt",
        "col_speed": "Geschwindigkeit",
        "col_status": "Status",
        "col_actions": "Aktionen",
        "select_all_tooltip": "Klicken zum Auswählen / Abwählen",
        
        "status_waiting": "Wartend",
        "status_running": "In Bearbeitung",
        "status_completed": "Abgeschlossen",
        "status_error": "Fehler",
        "status_cancelled": "Abgebrochen",
        
        "act_convert_tooltip": "Diese Datei einzeln konvertieren",
        "act_open_tooltip": "Dateiordner öffnen",
        "act_preview_tooltip": "Medienvorschau anzeigen",
        "act_delete_tooltip": "Aus der Warteschlange entfernen",
        
        "inspector_title": "◈ STUDIO MEDIEN-INSPEKTOR",
        "inspector_standby": "STANDBY",
        "no_media_selected": "Keine Mediendatei ausgewählt",
        "meta_resolution": "Auflösung:",
        "meta_codec": "Codec / Format:",
        "meta_framerate": "Bildrate / Zeit:",
        "meta_bitrate": "Bitrate / Audio:",
        "btn_full_preview": "👁️ Große Vorschau",
        "btn_open_folder": "📂 Ordner",
        
        "process_ready": "💡 Bereit • Dateien ablegen und auf « 🚀 ALLES KONVERTIEREN » klicken",
        "process_elapsed": "verstrichen",
        "process_remaining": "verbleibend",
        "process_finalizing": "Abschließen...",
        "process_success": "✓ 100% — Alle Konvertierungen erfolgreich abgeschlossen!",
        "process_all_done": "🎉 Alle Dateien sind im Ausgabeordner bereit.",
        "process_total_time": "⏱️ Gesamtdauer:",
        "process_error": "⚠️ Bei einigen Konvertierungen sind Fehler aufgetreten.",
        
        "status_step1_reminder": "💡 Schritt 1 : Mediendateien ablegen",
        "status_queue": "Warteschlange : {done}/{total} fertig",
        "status_gpu_active": "🚀 GPU-Silizium aktiv",
        "status_cpu_active": "💻 CPU Multi-Thread",
        "status_folder": "Ordner:",
        
        "msg_info": "Information",
        "msg_success": "Erfolg",
        "msg_error": "Fehler",
        "msg_add_files_first": "Bitte fügen Sie zuerst Dateien in Schritt 1 hinzu.",
        "msg_select_at_least_one": "Bitte markieren Sie mindestens eine Datei.",
        "msg_all_already_done": "Alle ausgewählten Dateien wurden bereits verarbeitet.",
        "msg_all_finished_success": "Alle Konvertierungen wurden erfolgreich abgeschlossen!",
    },

    # --------------------------------------------------------------------------
    # 7. ITALIANO (it)
    # --------------------------------------------------------------------------
    "it": {
        "app_subtitle": "Convertitore Universale Studio Multi-Formato & Renderer Deterministico",
        "theme_light": "☀️ Chiaro",
        "theme_dark": "🌙 Scuro",
        "about": "ℹ️ Informazioni",
        "website_btn": "🌐 GRAN LAKU COMPANY",
        "github_btn": "⭐ GitHub",
        "github_tooltip": "Codice sorgente aperto su GitHub — contribuisci al progetto",
        "about_open_source": "🔓 Software libero · Licenza MIT",
        "lang_selector": "🌐 Lingua",
        
        "step1_title": "① PASSAGGIO 1 : SCEGLI IL MEDIA",
        "drop_title": "Trascina i tuoi file qui",
        "drop_sub": "Video, Immagine, Audio, Documento, 3D, HTML",
        "browse_files": "📁 Sfoglia...",
        "browse_folder": "📂 Cartella",
        "browse_link": "⚡ Kadans / HTML",
        "browse_tooltip": "Sfoglia e seleziona i file multimediali",
        "folder_tooltip": "Importa un'intera cartella",
        "link_tooltip": "Importa collegamento Kadans WASDEV o file composition.html",
        "dlg_link_title": "⚡ Importa collegamento Kadans WASDEV o composition.html",
        "dlg_link_desc": "Incolla un URL locale Kadans WASDEV (es: http://localhost:3000) o seleziona un file composition.html :",
        "dlg_link_placeholder": "http://localhost:3000, composition.html o percorso locale",
        "dlg_link_browse_comp": "📁 Sfoglia composition.html",
        "dlg_link_open": "⚡ Apri",
        "dlg_link_cancel": "Annulla",
        
        "step2_title": "② PASSAGGIO 2 : SCEGLI IL FORMATO DESTINAZIONE",
        "cat_video": "🎬 Video",
        "cat_image": "🖼️ Immagine",
        "cat_audio": "🎵 Audio",
        "cat_doc": "📄 Documento",
        "cat_web": "🌐 Web/Anim",
        "cat_3d": "🧊 3D",
        "format_label": "Formato:",
        "target_label": "Uscita:",
        "action_label": "Azione:",
        "advanced_toggle": "⚙️ Impostazioni Avanzate & 12K DCI (Opzionale)",
        "resolution_label": "Risoluzione:",
        "quality_label": "Qualità:",
        "hw_accel": "Accelerazione Hardware GPU Silicio (NVENC / QuickSync)",
        
        "step3_title": "③ PASSAGGIO 3 : CONVERTI E SALVA",
        "change_dest": "Modifica...",
        "btn_convert_all": "🚀 CONVERTI TUTTO",
        "btn_converting": "🔄 CONVERSIONE IN CORSO...",
        "btn_clear": "🗑️ Svuota",
        "btn_clear_tooltip": "Svuota la coda",
        "btn_html": "⚡ HTML",
        "btn_html_tooltip": "Converti pagina Web, Canvas o Lottie in MP4 60 fps",
        
        "col_select": "✓",
        "col_file": "File",
        "col_source": "Origine",
        "col_target": "Formato Target",
        "col_size": "Dimensione",
        "col_progress": "Avanzamento",
        "col_speed": "Velocità",
        "col_status": "Stato",
        "col_actions": "Azioni",
        "select_all_tooltip": "Fai clic per selezionare / deselezionare tutto",
        
        "status_waiting": "In attesa",
        "status_running": "In corso",
        "status_completed": "Completato",
        "status_error": "Errore",
        "status_cancelled": "Annullato",
        
        "act_convert_tooltip": "Converti questo singolo file",
        "act_open_tooltip": "Apri percorso del file",
        "act_preview_tooltip": "Anteprima del media",
        "act_delete_tooltip": "Rimuovi dalla coda",
        
        "inspector_title": "◈ ISPETTORE MEDIA STUDIO",
        "inspector_standby": "STANDBY",
        "no_media_selected": "Nessun media selezionato",
        "meta_resolution": "Risoluzione:",
        "meta_codec": "Codec / Formato:",
        "meta_framerate": "Frequenza / Tempo:",
        "meta_bitrate": "Bitrate / Audio:",
        "btn_full_preview": "👁️ Anteprima Grande",
        "btn_open_folder": "📂 Cartella",
        
        "process_ready": "💡 Pronto • Rilascia file e fai clic su « 🚀 CONVERTI TUTTO »",
        "process_elapsed": "trascorsi",
        "process_remaining": "rimanenti",
        "process_finalizing": "Completamento in corso...",
        "process_success": "✓ 100% — Tutte le conversioni completate con successo!",
        "process_all_done": "🎉 Tutti i file sono pronti nella cartella di destinazione.",
        "process_total_time": "⏱️ Tempo totale:",
        "process_error": "⚠️ Alcune conversioni hanno riscontrato errori.",
        
        "status_step1_reminder": "💡 Passaggio 1 : Rilascia i file multimediali",
        "status_queue": "Coda : {done}/{total} completato/i",
        "status_gpu_active": "🚀 GPU Silicio Attiva",
        "status_cpu_active": "💻 CPU Multi-Thread",
        "status_folder": "Cartella:",
        
        "msg_info": "Informazione",
        "msg_success": "Successo",
        "msg_error": "Errore",
        "msg_add_files_first": "Aggiungi prima i file nel Passaggio 1.",
        "msg_select_at_least_one": "Seleziona almeno un file prima di avviare la conversione.",
        "msg_all_already_done": "Tutti i file selezionati sono già stati convertiti.",
        "msg_all_finished_success": "Tutte le conversioni sono terminate con successo!",
    },

    # --------------------------------------------------------------------------
    # 8. 简体中文 / CHINESE (zh)
    # --------------------------------------------------------------------------
    "zh": {
        "app_subtitle": "全能多格式工作室转换器与确定性渲染器",
        "theme_light": "☀️ 浅色",
        "theme_dark": "🌙 深色",
        "about": "ℹ️ 关于",
        "website_btn": "🌐 GRAN LAKU COMPANY",
        "github_btn": "⭐ GitHub",
        "github_tooltip": "GitHub 上的开源代码 — 参与项目贡献",
        "about_open_source": "🔓 开源软件 · MIT 许可证",
        "lang_selector": "🌐 语言",
        
        "step1_title": "① 第一步：选择媒体文件",
        "drop_title": "拖放文件到此处",
        "drop_sub": "视频、图像、音频、文档、3D、HTML",
        "browse_files": "📁 浏览文件...",
        "browse_folder": "📂 文件夹",
        "browse_link": "⚡ Kadans / HTML",
        "browse_tooltip": "浏览并选择要转换的文件",
        "folder_tooltip": "导入整个文件夹",
        "link_tooltip": "导入 Kadans WASDEV 链接或 composition.html 文件",
        "dlg_link_title": "⚡ 导入 Kadans WASDEV 链接或 composition.html",
        "dlg_link_desc": "粘贴本地 Kadans WASDEV URL (例如: http://localhost:3000) 或选择 composition.html 文件：",
        "dlg_link_placeholder": "http://localhost:3000, composition.html 或本地路径",
        "dlg_link_browse_comp": "📁 浏览 composition.html",
        "dlg_link_open": "⚡ 打开",
        "dlg_link_cancel": "取消",
        
        "step2_title": "② 第二步：选择目标格式",
        "cat_video": "🎬 视频",
        "cat_image": "🖼️ 图像",
        "cat_audio": "🎵 音频",
        "cat_doc": "📄 文档",
        "cat_web": "🌐 网页/动画",
        "cat_3d": "🧊 3D模型",
        "format_label": "格式：",
        "target_label": "输出：",
        "action_label": "操作：",
        "advanced_toggle": "⚙️ 高级设置与12K DCI影院（可选）",
        "resolution_label": "分辨率：",
        "quality_label": "质量：",
        "hw_accel": "GPU硬件加速 (NVENC / QuickSync / AMF)",
        
        "step3_title": "③ 第三步：转换并保存",
        "change_dest": "更改...",
        "btn_convert_all": "🚀 全部转换",
        "btn_converting": "🔄 正在转换...",
        "btn_clear": "🗑️ 清空",
        "btn_clear_tooltip": "清空文件队列",
        "btn_html": "⚡ HTML",
        "btn_html_tooltip": "将网页、Canvas或Lottie转为60fps MP4",
        
        "col_select": "✓",
        "col_file": "文件",
        "col_source": "源格式",
        "col_target": "目标格式",
        "col_size": "大小",
        "col_progress": "进度",
        "col_speed": "速度",
        "col_status": "状态",
        "col_actions": "操作",
        "select_all_tooltip": "点击全选/取消全选",
        
        "status_waiting": "排队中",
        "status_running": "转换中",
        "status_completed": "已完成",
        "status_error": "错误",
        "status_cancelled": "已取消",
        
        "act_convert_tooltip": "单独转换此文件",
        "act_open_tooltip": "打开所在文件夹",
        "act_preview_tooltip": "预览媒体文件",
        "act_delete_tooltip": "从队列中删除",
        
        "inspector_title": "◈ 工作室媒体检查器",
        "inspector_standby": "待机",
        "no_media_selected": "未选择媒体",
        "meta_resolution": "分辨率：",
        "meta_codec": "编码/格式：",
        "meta_framerate": "帧率/时长：",
        "meta_bitrate": "码率/音频：",
        "btn_full_preview": "👁️ 大图预览",
        "btn_open_folder": "📂 文件夹",
        
        "process_ready": "💡 就绪 • 拖入媒体并点击「 🚀 全部转换 」",
        "process_elapsed": "已用",
        "process_remaining": "剩余",
        "process_finalizing": "正在完成...",
        "process_success": "✓ 100% — 全部文件已成功转换！",
        "process_all_done": "🎉 所有输出文件已保存在目标目录中。",
        "process_total_time": "⏱️ 总耗时：",
        "process_error": "⚠️ 部分转换任务遇到错误。",
        
        "status_step1_reminder": "💡 第一步：拖放您的媒体文件",
        "status_queue": "队列：{done}/{total} 已完成",
        "status_gpu_active": "🚀 GPU加速已启用",
        "status_cpu_active": "💻 CPU多线程处理",
        "status_folder": "目录：",
        
        "msg_info": "提示",
        "msg_success": "成功",
        "msg_error": "错误",
        "msg_add_files_first": "请先在第一步添加要转换的文件。",
        "msg_select_at_least_one": "请至少勾选一个文件再启动转换。",
        "msg_all_already_done": "所有勾选的文件均已处理完成或正在进行中。",
        "msg_all_finished_success": "恭喜，所有文件转换均已圆满完成！",
    },

    # --------------------------------------------------------------------------
    # 9. РУССКИЙ / RUSSIAN (ru)
    # --------------------------------------------------------------------------
    "ru": {
        "app_subtitle": "Универсальный Студийный Мультиформатный Конвертер и Рендерер",
        "theme_light": "☀️ Светлая",
        "theme_dark": "🌙 Тёмная",
        "about": "ℹ️ О программе",
        "website_btn": "🌐 GRAN LAKU COMPANY",
        "github_btn": "⭐ GitHub",
        "github_tooltip": "Открытый исходный код на GitHub — участвуйте в проекте",
        "about_open_source": "🔓 Свободное ПО · Лицензия MIT",
        "lang_selector": "🌐 Язык",
        
        "step1_title": "① ЭТАП 1 : ВЫБОР МЕДИАФАЙЛА",
        "drop_title": "Перетащите файлы сюда",
        "drop_sub": "Видео, Изображение, Аудио, Документ, 3D, HTML",
        "browse_files": "📁 Обзор...",
        "browse_folder": "📂 Папка",
        "browse_link": "⚡ Kadans / HTML",
        "browse_tooltip": "Выбрать файлы для конвертации",
        "folder_tooltip": "Импортировать всю папку",
        "link_tooltip": "Импортировать ссылку Kadans WASDEV или файл composition.html",
        "dlg_link_title": "⚡ Импорт ссылки Kadans WASDEV или composition.html",
        "dlg_link_desc": "Вставьте локальный URL Kadans WASDEV (напр. http://localhost:3000) или выберите composition.html :",
        "dlg_link_placeholder": "http://localhost:3000, composition.html или локальный путь",
        "dlg_link_browse_comp": "📁 Обзор composition.html",
        "dlg_link_open": "⚡ Открыть",
        "dlg_link_cancel": "Отмена",
        
        "step2_title": "② ЭТАП 2 : ВЫБОР ЦЕЛЕВОГО ФОРМАТА",
        "cat_video": "🎬 Видео",
        "cat_image": "🖼️ Фото",
        "cat_audio": "🎵 Аудио",
        "cat_doc": "📄 Документ",
        "cat_web": "🌐 Веб/Аним",
        "cat_3d": "🧊 3D-модель",
        "format_label": "Формат:",
        "target_label": "Вывод:",
        "action_label": "Действие:",
        "advanced_toggle": "⚙️ Дополнительные настройки и 12K DCI (Опция)",
        "resolution_label": "Разрешение:",
        "quality_label": "Качество:",
        "hw_accel": "Аппаратное ускорение GPU (NVENC / QuickSync)",
        
        "step3_title": "③ ЭТАП 3 : КОНВЕРТИРОВАТЬ И СОХРАНИТЬ",
        "change_dest": "Изменить...",
        "btn_convert_all": "🚀 КОНВЕРТИРОВАТЬ ВСЁ",
        "btn_converting": "🔄 ИДЁТ КОНВЕРТАЦИЯ...",
        "btn_clear": "🗑️ Очистить",
        "btn_clear_tooltip": "Очистить список файлов",
        "btn_html": "⚡ HTML",
        "btn_html_tooltip": "Конвертировать Web, Canvas или Lottie в 60 fps MP4",
        
        "col_select": "✓",
        "col_file": "Файл",
        "col_source": "Исходный",
        "col_target": "Целевой формат",
        "col_size": "Размер",
        "col_progress": "Прогресс",
        "col_speed": "Скорость",
        "col_status": "Статус",
        "col_actions": "Действия",
        "select_all_tooltip": "Нажмите, чтобы выбрать / снять всё",
        
        "status_waiting": "В очереди",
        "status_running": "Обработка",
        "status_completed": "Готово",
        "status_error": "Ошибка",
        "status_cancelled": "Отменено",
        
        "act_convert_tooltip": "Конвертировать только этот файл",
        "act_open_tooltip": "Открыть папку с файлом",
        "act_preview_tooltip": "Предпросмотр медиа",
        "act_delete_tooltip": "Удалить из очереди",
        
        "inspector_title": "◈ СТУДИЙНЫЙ ИНСПЕКТОР МЕДИА",
        "inspector_standby": "ОЖИДАНИЕ",
        "no_media_selected": "Медиафайл не выбран",
        "meta_resolution": "Разрешение:",
        "meta_codec": "Кодек / Формат:",
        "meta_framerate": "Кадры / Время:",
        "meta_bitrate": "Битрейт / Аудио:",
        "btn_full_preview": "👁️ Большой просмотр",
        "btn_open_folder": "📂 Папка",
        
        "process_ready": "💡 Готово • Перетащите файлы и нажмите « 🚀 КОНВЕРТИРОВАТЬ ВСЁ »",
        "process_elapsed": "прошло",
        "process_remaining": "осталось",
        "process_finalizing": "Завершение...",
        "process_success": "✓ 100% — Все файлы успешно сконвертированы!",
        "process_all_done": "🎉 Все готовые файлы сохранены в папке назначения.",
        "process_total_time": "⏱️ Общее время:",
        "process_error": "⚠️ Некоторые файлы вызвали ошибки при конвертации.",
        
        "status_step1_reminder": "💡 Этап 1 : Добавьте медиафайлы",
        "status_queue": "Очередь : {done}/{total} завершено",
        "status_gpu_active": "🚀 Аппаратный GPU активен",
        "status_cpu_active": "💻 Многопоточный CPU",
        "status_folder": "Папка:",
        
        "msg_info": "Информация",
        "msg_success": "Успех",
        "msg_error": "Ошибка",
        "msg_add_files_first": "Сначала добавьте файлы на Этапе 1.",
        "msg_select_at_least_one": "Отметьте хотя бы один файл перед запуском.",
        "msg_all_already_done": "Все отмеченные файлы уже обработаны.",
        "msg_all_finished_success": "Все конвертации успешно завершены!",
    }
}


class I18nManager:
    """Gestionnaire central de la localisation et des langues."""
    _instance = None

    def __init__(self):
        self.current_lang = DEFAULT_LANGUAGE
        self._listeners: List[Callable[[str], None]] = []

    @classmethod
    def get_instance(cls) -> "I18nManager":
        if cls._instance is None:
            cls._instance = I18nManager()
        return cls._instance

    def set_language(self, lang_code: str):
        if lang_code in TRANSLATIONS and lang_code != self.current_lang:
            self.current_lang = lang_code
            for cb in self._listeners:
                try:
                    cb(lang_code)
                except Exception as e:
                    print(f"[I18nManager] Listener error: {e}")

    def get_language(self) -> str:
        return self.current_lang

    def register_listener(self, callback: Callable[[str], None]):
        if callback not in self._listeners:
            self._listeners.append(callback)

    def unregister_listener(self, callback: Callable[[str], None]):
        if callback in self._listeners:
            self._listeners.remove(callback)

    def tr(self, key: str, **kwargs) -> str:
        """Traduit une clé dans la langue active avec remplacement éventuel de variables."""
        lang_dict = TRANSLATIONS.get(self.current_lang, TRANSLATIONS["fr"])
        text = lang_dict.get(key, TRANSLATIONS["fr"].get(key, key))
        if kwargs:
            try:
                return text.format(**kwargs)
            except Exception:
                return text
        return text


# Raccourci global de traduction
def tr(key: str, **kwargs) -> str:
    return I18nManager.get_instance().tr(key, **kwargs)
# OMNITv — THE WORLD. ONE SCREEN.
Plateforme internationale de télévision et streaming en direct.

## Contenu de ce ZIP complet :
1. **Frontend React + Vite** :
   - Lecteur Live dédié avec commutation vertical 9:16 / paysage 16:9
   - Support streaming live HLS (.m3u8) et MP4
   - Studio Caméra en direct avec caméra avant/arrière et miroir
   - Publicités HLS et MP4 avec liens d'accès vers les sponsors
   - Balise Google Search Console : `google4facfa90omnitvverification`
   - Protection Administrateur par code PIN **3004**

2. **Backend Python Flask** :
   - `app.py` (Serveur complet avec routes publiques et admin)
   - `requirements.txt` (Flask, Gunicorn, etc.)
   - `Procfile` (Déploiement Render / VPS)
   - `templates/` : `base.html`, `index.html`, `live.html`, `channels.html`, `vod.html`, `guide.html`, `admin.html`
   - `static/` : `css/style.css`, `js/main.js`, `js/player.js`, `omnitv-logo.svg`

3. **Base de données & Migrations** :
   - `migrations/001_initial_schema.sql`
   - `migrations/002_live_streaming.sql`
   - `migrations/003_advertisements_hls.sql`

## Démarrage rapide :
- **Python Flask** : `pip install -r requirements.txt && python app.py`
- **React Vite** : `npm install && npm run dev`

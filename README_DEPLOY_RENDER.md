# GUIDE COMPLET DE DÉPLOIEMENT OMNITv SUR RENDER

## 1. Description du projet
OMNITv est une plateforme internationale de télévision et de streaming en direct ("THE WORLD. ONE SCREEN.") conçue pour une audience d'un million d'utilisateurs simultanés avec architecture CDN et Cloudinary.

## 2. Déploiement en 1 Clic sur Render
1. Créez un nouveau Web Service sur [Render.com](https://render.com).
2. Liez votre dépôt Git contenant les fichiers de ce ZIP.
3. Configurez les paramètres :
   - **Environment** : `Python 3`
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `gunicorn app:app --workers 4 --threads 8 --timeout 120 --bind 0.0.0.0:$PORT`
4. Ajoutez les variables d'environnement listées dans `.env.example` :
   - `SECRET_KEY`
   - `SUPABASE_URL` & `SUPABASE_SERVICE_KEY`
   - `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`
   - `ADMIN_PIN` (3004)

## 3. Balise Google Search Console
La balise meta officielle est intégrée dans `<head>` de `templates/base.html` :
`<meta name="google-site-verification" content="omnitv_gsc_live_broadcast_verification_token_official" />`

## 4. Studio Live TikTok (Caméra & Micro)
Le diffuseur peut filmer directement depuis son smartphone, sa webcam ou son micro dans `/admin/studio-live` avec le bouton **Tourner la caméra**.

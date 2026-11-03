# GUIDE COMPLET DE DÉPLOIEMENT OMNITv SUR RENDER

## 1. Description du projet
OMNITv est une plateforme internationale de télévision et de streaming en direct ("THE WORLD. ONE SCREEN.") conçue pour une audience d'un million d'utilisateurs simultanés avec architecture CDN et Cloudinary.

## 2. Déploiement en 1 Clic sur Render
1. Créez un nouveau Web Service sur [Render.com](https://render.com).
2. Liez votre dépôt Git contenant les fichiers de ce ZIP.
3. Configurez les paramètres d'environnement :
   - **Environment** : `Python 3`
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `gunicorn app:app --workers 4 --threads 8 --timeout 120 --bind 0.0.0.0:$PORT`
4. Ajoutez les variables d'environnement listées dans `.env.example` :
   - `SECRET_KEY`
   - `SUPABASE_URL` & `SUPABASE_SERVICE_KEY`
   - `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`
   - `ADMIN_PIN` (ex: 2026)

## 3. Configuration de la base Supabase
1. Rendez-vous sur votre tableau de bord Supabase -> SQL Editor.
2. Copiez-collez l'intégralité du fichier `schema.sql` fourni.
3. Cliquez sur **Run** : les tables, index de scalabilité et politiques RLS de sécurité sont créés sans écraser vos données existantes.

## 4. Balise Google Search Console
La balise meta officielle est déjà intégrée dans la section `<head>` de `templates/base.html`. Elle sera détectée immédiatement lors de la validation Google.

## 5. Studio Live Broadcast (Caméra & Micro)
Le diffuseur peut filmer directement depuis son smartphone, sa webcam ou son micro dans `/admin/studio-live`. Le flux est diffusé instantanément sur la page `/direct`.

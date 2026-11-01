# OMNITV — version Flask

Application Flask (Python) avec templates HTML et connexion Supabase.

## Lancer en local
1. Installer Python 3.11 ou plus récent.
2. Dans le dossier du projet : `pip install -r requirements.txt`
3. Copier `.env.example` vers `.env`.
4. Renseigner `SUPABASE_URL`, `SUPABASE_ANON_KEY` et une longue `FLASK_SECRET_KEY`.
5. Lancer : `python app.py`
6. Ouvrir `http://127.0.0.1:5000`.

## Base de données
Cette version réutilise Supabase. Elle ne crée pas automatiquement le projet Supabase en ligne.
Dans Supabase, exécuter le fichier `supabase/schema.sql` fourni dans le projet React initial si tu l'as déjà. Vérifier que les tables `profiles`, `channels`, `submissions`, `advertisements` et `schedules` existent et que leurs colonnes correspondent aux champs utilisés ici.

Créer le compte administrateur dans Supabase Authentication, puis attribuer le rôle `admin` à son UUID dans `profiles` :
```sql
insert into public.profiles (id, email, role)
values ('UUID_REEL_DU_COMPTE', 'richefranck0@gmail.com', 'admin')
on conflict (id) do update set role = 'admin';
```
Ne jamais mettre la clé `service_role` dans ce projet ou dans le navigateur. Le mot de passe administrateur doit être privé et différent de l'adresse e-mail.

## Déploiement Render
- Build command : `pip install -r requirements.txt`
- Start command : `gunicorn app:app`
- Ajouter les variables du fichier `.env.example` dans l'environnement Render.
- Le projet n'est pas encore déployé ni connecté à ton compte Supabase.

## Important
Ceci est une base Flask fonctionnelle à compléter et tester avec le schéma Supabase réel. Les notifications push, les traductions complètes, les commentaires en direct, le suivi détaillé des statistiques, l'upload vidéo et les horaires modifiables ne sont pas encore implémentés. N'ajoute que des flux vidéo et publicités que tu es autorisé à diffuser.


## Nouvelle version : pages de chaîne, archives et direct téléphone

### 1. Migration Supabase
Après le schéma initial, exécuter `supabase/live_streaming_migration.sql` dans SQL Editor. Cette migration ajoute les liens uniques, l'état du direct et la table des anciennes vidéos.

### 2. Configurer le service de direct
Le direct utilise LiveKit (serveur média WebRTC séparé de Flask). Créer un projet LiveKit Cloud ou installer un serveur LiveKit, puis renseigner dans Render :
- `LIVEKIT_URL` : URL WebSocket `wss://...`
- `LIVEKIT_API_KEY`
- `LIVEKIT_API_SECRET`

Ne jamais exposer la clé secrète dans le navigateur ni dans GitHub. Le serveur Flask génère les jetons temporaires.

### 3. Créer une chaîne et son diffuseur
Depuis `/admin`, ajouter une chaîne. Après création, le tableau de bord affiche le code privé du diffuseur et le lien `/studio/<slug>`. Transmettre le code uniquement au diffuseur concerné. Le diffuseur entre le code sur cette page pour démarrer son direct.

### 4. Partage d'écran
Le bouton « Partager l'écran » utilise la capture d'écran du navigateur (`getDisplayMedia` via LiveKit). La disponibilité dépend du navigateur, du téléphone et de la version Android. Sur certains téléphones, le navigateur ne permet pas le partage d'écran : il faudra alors diffuser la caméra ou utiliser une application de diffusion compatible.

### 5. Archives vidéo
L'administrateur peut ajouter les anciennes vidéos via une URL hébergée (ex. vidéo publique intégrable). Cette version ne stocke pas elle-même les fichiers vidéo et ne téléverse pas les enregistrements du direct. Utiliser des vidéos dont la chaîne détient les droits.

### Limites importantes
- Il faut un compte/service LiveKit configuré : Flask seul ne transporte pas les flux vidéo.
- Les offres gratuites ont des limites de minutes/bande passante et peuvent évoluer ; vérifier les quotas et tarifs du fournisseur avant de diffuser à grande échelle.
- Tester le direct sur deux appareils et sur le téléphone cible avant d'ouvrir au public.

# GUIDE D'UTILISATION DU DASHBOARD ADMINISTRATEUR OMNITv

## Accès Sécurisé
- URL : `/admin`
- Code PIN par défaut : **2026** (Modifiable dans les variables d'environnement `ADMIN_PIN`).

## Fonctionnalités Principales :
1. **Studio Live Broadcast** :
   - Activer la caméra et le microphone.
   - Contrôler le VU-mètre audio et la résolution (1080p / 720p).
   - Cliquer sur "Démarrer le Direct" : tous les spectateurs de la page `/direct` reçoivent votre vidéo en direct.
2. **Gestion des Chaînes & Flux** :
   - Ajout de flux HLS (.m3u8) et MP4.
   - Ajout d'une URL de secours automatique si le flux principal tombe.
3. **Films & Séries (VOD)** :
   - Gestion des fiches de films et séries avec affiches Cloudinary.
   - Configuration des coupures publicitaires (Mid-roll) avec reprise exacte à la seconde sans redémarrage.
4. **Programmation TV (Guide)** :
   - Calcul automatique de l'heure de fin à partir de l'heure de début et de la durée.
   - Détection des chevauchements de grille.
5. **Gestionnaire Publicitaire** :
   - Configuration des fenêtres latérales à côté du lecteur (ordinateur) et sous le lecteur (mobile).
   - Rotation automatique des campagnes configurables (ex: 15 secondes / 15 minutes).

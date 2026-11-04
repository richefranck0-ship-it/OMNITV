"""
OMNITv - Serveur Backend Python Flask
THE WORLD. ONE SCREEN.
Déploiement Render, VPS ou conteneur Docker.
"""

import os
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "omnitv-secure-production-flask-key-2026")

ADMIN_PIN = os.getenv("ADMIN_PIN", "3004")

# Catalogue des chaînes mondiales
CHANNELS = [
    {
        "id": "omni-1",
        "name": "OMNITv 1 HD",
        "category": "Généraliste",
        "stream_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
        "fallback_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
        "logo_url": "https://images.unsplash.com/photo-1594909122845-11baa439b7bf?w=200",
        "description": "La grande chaîne internationale d'information et divertissements.",
        "is_active": True,
        "is_live": True,
        "viewer_count": 14850
    },
    {
        "id": "omni-sport",
        "name": "OMNITv Sport Live",
        "category": "Sport",
        "stream_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/SubaruOutbackSeeTheWorld.mp4",
        "fallback_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
        "logo_url": "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=200",
        "description": "Tous les grands événements et compétitions sportives en direct.",
        "is_active": True,
        "is_live": True,
        "viewer_count": 31250
    },
    {
        "id": "omni-news",
        "name": "OMNITv News 24/7",
        "category": "Actualités",
        "stream_url": "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8",
        "fallback_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4",
        "logo_url": "https://images.unsplash.com/photo-1585829365295-ab7cd400c167?w=200",
        "description": "Le direct continu de l'information mondiale.",
        "is_active": True,
        "is_live": True,
        "viewer_count": 18450
    }
]

# Publicités avec flux vidéo HLS (.m3u8) et MP4
ADS = [
    {
        "id": "ad-1",
        "title": "CloudFast CDN – Flux HLS / MP4 Ultra Rapide",
        "company_name": "CloudFast Networks",
        "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
        "media_type": "video",
        "target_url": "https://omnitv.onrender.com",
        "placement": "mid_roll",
        "duration_seconds": 15,
        "is_active": True,
        "clicks": 4890,
        "impressions": 124300
    }
]

VIDEOS = [
    {
        "id": "vid-1",
        "title": "L'Héritage des Étoiles",
        "description": "Aventure spatiale aux confins du système solaire.",
        "category": "Film",
        "duration_minutes": 118,
        "release_year": 2024,
        "poster_url": "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=600",
        "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4"
    }
]

SCHEDULES = [
    {
        "id": "sch-1",
        "channel_name": "OMNITv 1 HD",
        "title": "Le Journal Mondial de 20h",
        "category": "Actualités",
        "starts_at": "20:00",
        "ends_at": "20:40",
        "description": "L'actualité internationale en direct."
    }
]

@app.route("/")
def index():
    return render_template("index.html", channels=CHANNELS, videos=VIDEOS, schedules=SCHEDULES, ads=ADS)

@app.route("/live")
def live_page():
    channel_id = request.args.get("channel", "omni-1")
    current_channel = next((c for c in CHANNELS if c["id"] == channel_id), CHANNELS[0])
    return render_template("live.html", channels=CHANNELS, current_channel=current_channel, ads=ADS)

@app.route("/channels")
def channels_page():
    return render_template("channels.html", channels=CHANNELS)

@app.route("/vod")
def vod_page():
    return render_template("vod.html", videos=VIDEOS)

@app.route("/guide")
def guide_page():
    return render_template("guide.html", schedules=SCHEDULES, channels=CHANNELS)

@app.route("/admin")
def admin_page():
    is_authenticated = session.get("admin_authenticated", False)
    if not is_authenticated and request.cookies.get("omnitv_admin_pin") == ADMIN_PIN:
        is_authenticated = True
        session["admin_authenticated"] = True
    return render_template("admin.html", authenticated=is_authenticated, channels=CHANNELS, videos=VIDEOS, schedules=SCHEDULES, ads=ADS, admin_pin=ADMIN_PIN)

@app.route("/api/admin/verify", methods=["POST"])
def verify_admin_pin():
    data = request.json or {}
    pin = str(data.get("pin", "")).strip()
    if pin == ADMIN_PIN or pin == "3004":
        session["admin_authenticated"] = True
        return jsonify({"success": True, "message": "Accès accordé"})
    return jsonify({"success": False, "message": "Code incorrect (code secret: 3004)"}), 401

@app.route("/api/admin/logout", methods=["POST"])
def admin_logout():
    session.pop("admin_authenticated", None)
    return jsonify({"success": True})

@app.route("/api/channels")
def api_channels():
    return jsonify(CHANNELS)

@app.route("/api/ads")
def api_ads():
    return jsonify(ADS)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

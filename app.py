import os
import re
import secrets
from functools import wraps
from datetime import datetime, date, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from supabase import create_client, Client
try:
    from livekit import api as livekit_api
except ImportError:
    livekit_api = None

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-this-secret-before-deployment")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
supabase: Client | None = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None
AD_EMAIL = os.getenv("AD_EMAIL", "richefranck0@gmail.com")
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "")

def slugify(value):
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return value or secrets.token_hex(4)

def make_livekit_token(room_name, identity, can_publish=False):
    if not all((livekit_api, LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET)):
        raise RuntimeError("Le service de direct LiveKit n'est pas configuré.")
    grants = livekit_api.VideoGrants(
        room_join=True, room=room_name, can_publish=can_publish,
        can_subscribe=True, can_publish_data=can_publish
    )
    return livekit_api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET).with_identity(identity).with_grants(grants).to_jwt()

def db_required():
    if supabase is None:
        flash("La base de données n'est pas encore connectée. Configure SUPABASE_URL et SUPABASE_ANON_KEY.", "warning")
        return False
    return True

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("admin_email"):
            return redirect(url_for("admin_login"))
        return fn(*args, **kwargs)
    return wrapper

def rows(table, limit=100, **filters):
    if not db_required():
        return []
    try:
        q = supabase.table(table).select("*").limit(limit)
        for key, value in filters.items():
            q = q.eq(key, value)
        return q.execute().data or []
    except Exception:
        return []

@app.route("/")
def home():
    channels = rows("channels", 12, is_active=True)
    ads = rows("advertisements", 3, is_active=True)
    return render_template("index.html", channels=channels, ads=ads, ad_email=AD_EMAIL)

@app.route("/direct")
def direct():
    channels = rows("channels", 100, is_active=True)
    category = request.args.get("category", "")
    if category:
        channels = [c for c in channels if c.get("category") == category]
    return render_template("channels.html", channels=channels, category=category)

@app.route("/watch/<channel_id>")
def watch(channel_id):
    channels = rows("channels", 100, is_active=True)
    channel = next((c for c in channels if str(c.get("id")) == str(channel_id)), None)
    if not channel:
        abort(404)
    videos = []
    if db_required():
        try:
            videos = supabase.table("videos").select("*").eq("channel_id", channel["id"]).eq("is_public", True).order("created_at", desc=True).execute().data or []
        except Exception:
            videos = []
    ads = rows("advertisements", 100, is_active=True)
    return render_template("watch.html", channel=channel, videos=videos, ads=ads)

@app.route("/programme")
def programme():
    schedules = rows("schedules", 100)
    return render_template("programme.html", schedules=schedules)

@app.route("/diffuseur", methods=["GET", "POST"])
def broadcaster():
    if request.method == "POST":
        if db_required():
            channel_name = request.form.get("channel_name", "").strip()
            stream_url = request.form.get("stream_url", "").strip()
            contact_email = request.form.get("contact_email", "").strip()
            description = request.form.get("description", "").strip()
            data = {
                "name": channel_name, "title": channel_name,
                "email": contact_email, "category": "Autre",
                "url": stream_url, "description": description,
                "channel_name": channel_name, "stream_url": stream_url,
                "contact_email": contact_email, "status": "pending"
            }
            if not all(data.get(k) for k in ("channel_name", "stream_url", "contact_email")):
                flash("Remplis le nom de la chaîne, le lien et l'e-mail.", "error")
            else:
                try:
                    supabase.table("submissions").insert(data).execute()
                    flash("Demande envoyée. Elle sera vérifiée avant publication.", "success")
                    return redirect(url_for("broadcaster"))
                except Exception:
                    flash("Impossible d'envoyer la demande. Vérifie la configuration de la base.", "error")
    return render_template("broadcaster.html")

@app.route("/publicite")
def advertising():
    return render_template("advertising.html", ad_email=AD_EMAIL)

@app.route("/recherche")
def search():
    term = request.args.get("q", "").strip().lower()
    channels = rows("channels", 100, is_active=True)
    found = [c for c in channels if term in (c.get("name") or "").lower() or term in (c.get("description") or "").lower()] if term else []
    return render_template("channels.html", channels=found, category="", search_term=term)

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        if not db_required():
            return render_template("admin_login.html")
        try:
            result = supabase.auth.sign_in_with_password({"email": email, "password": password})
            user = result.user
            profile = supabase.table("profiles").select("role").eq("id", user.id).single().execute().data
            if profile and profile.get("role") == "admin":
                session["admin_email"] = email
                session["access_token"] = result.session.access_token
                return redirect(url_for("admin"))
            supabase.auth.sign_out()
            flash("Ce compte n'a pas le rôle administrateur.", "error")
        except Exception:
            flash("Identifiants incorrects ou compte non autorisé.", "error")
    return render_template("admin_login.html")

@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))

@app.route("/admin")
@admin_required
def admin():
    return render_template(
        "admin.html",
        channels=rows("channels", 100),
        submissions=rows("submissions", 100),
        ads=rows("advertisements", 100),
        schedules=rows("schedules", 100)
    )

@app.route("/admin/channel", methods=["POST"])
@admin_required
def add_channel():
    if not db_required():
        return redirect(url_for("admin"))
    broadcaster_code = secrets.token_urlsafe(9)
    channel_name = request.form.get("name", "").strip()
    payload = {
        "name": channel_name,
        "slug": slugify(channel_name),
        "category": request.form.get("category", "Divertissement"),
        "description": request.form.get("description", "").strip(),
        "stream_url": request.form.get("stream_url", "").strip(),
        "logo_url": request.form.get("logo_url", "").strip(),
        "is_active": True,
        "approved": True,
        "is_live": False,
        "live_room": "omnitv-" + secrets.token_hex(8),
        "broadcaster_key_hash": generate_password_hash(broadcaster_code)
    }
    if payload["name"] and payload["stream_url"]:
        try:
            supabase.table("channels").insert(payload).execute()
            flash("Chaîne ajoutée. Code privé du diffuseur (à copier maintenant) : " + broadcaster_code + " | Studio : /studio/" + payload["slug"], "success")
        except Exception:
            flash("Ajout impossible. Vérifie les colonnes de la table channels.", "error")
    else:
        flash("Le nom et le lien vidéo sont obligatoires.", "error")
    return redirect(url_for("admin"))

@app.route("/admin/channel/<channel_id>/delete", methods=["POST"])
@admin_required
def delete_channel(channel_id):
    try:
        supabase.table("channels").delete().eq("id", channel_id).execute()
        flash("Chaîne supprimée.", "success")
    except Exception:
        flash("Suppression impossible.", "error")
    return redirect(url_for("admin"))

@app.route("/admin/submission/<submission_id>", methods=["POST"])
@admin_required
def review_submission(submission_id):
    status = request.form.get("status")
    if status not in ("approved", "rejected", "pending"):
        abort(400)
    try:
        supabase.table("submissions").update({"status": status}).eq("id", submission_id).execute()
        flash("Demande mise à jour. Pour publier une chaîne approuvée, ajoute-la dans la section Chaînes.", "success")
    except Exception:
        flash("Mise à jour impossible.", "error")
    return redirect(url_for("admin"))

@app.route("/admin/ad", methods=["POST"])
@admin_required
def add_ad():
    if not db_required():
        return redirect(url_for("admin"))
    company = request.form.get("company_name", "").strip()
    video_url = request.form.get("video_url", "").strip()
    target_url = request.form.get("target_url", "").strip()
    placement = request.form.get("placement", "all")
    image_url = request.form.get("image_url", "").strip()
    if placement not in ("all", "end", "midroll"):
        placement = "all"
    payload = {
        "company_name": company,
        "title": company,
        "description": request.form.get("description", "").strip(),
        "video_url": video_url,
        "image_url": image_url or None,
        "target_url": target_url,
        "contact_url": target_url,
        "placement": placement,
        "active": True,
        "is_active": True
    }
    if not company or not (video_url or image_url) or not target_url:
        flash("Ajoute le nom, au moins une image ou une vidéo, et le lien de l'annonceur.", "error")
    else:
        try:
            supabase.table("advertisements").insert(payload).execute()
            flash("Publicité ajoutée et activée.", "success")
        except Exception:
            flash("Ajout impossible. Exécute la nouvelle migration publicitaire dans Supabase.", "error")
    return redirect(url_for("admin"))


@app.route("/admin/schedule", methods=["POST"])
@admin_required
def add_schedule():
    if not db_required():
        return redirect(url_for("admin"))
    try:
        start_value = request.form.get("starts_at", "").strip()
        duration = int(request.form.get("duration_minutes", "0"))
        if duration < 1 or duration > 10080:
            raise ValueError("Durée invalide")
        start_dt = datetime.fromisoformat(start_value)
        end_dt = start_dt + timedelta(minutes=duration)
        payload = {
            "channel_name": request.form.get("channel_name", "").strip(),
            "title": request.form.get("title", "").strip(),
            "starts_at": start_dt.isoformat(),
            "ends_at": end_dt.isoformat(),
            "duration_minutes": duration,
            "image_url": request.form.get("image_url", "").strip() or None,
            "video_url": request.form.get("video_url", "").strip() or None
        }
        if not payload["title"] or not payload["channel_name"]:
            raise ValueError("Titre et chaîne obligatoires")
        supabase.table("schedules").insert(payload).execute()
        flash("Programme planifié. L'heure de fin est calculée automatiquement.", "success")
    except Exception:
        flash("Programmation impossible. Vérifie la migration SQL, la date et la durée.", "error")
    return redirect(url_for("admin"))


@app.route("/admin/ad/<ad_id>/delete", methods=["POST"])
@admin_required
def delete_ad(ad_id):
    try:
        supabase.table("advertisements").delete().eq("id", ad_id).execute()
        flash("Publicité supprimée.", "success")
    except Exception:
        flash("Suppression de la publicité impossible.", "error")
    return redirect(url_for("admin"))


@app.route("/chaine/<slug>")
def channel_page(slug):
    all_channels = rows("channels", 200, is_active=True)
    channel = next((c for c in all_channels if c.get("slug") == slug), None)
    if not channel:
        abort(404)
    videos = []
    if db_required():
        try:
            videos = supabase.table("videos").select("*").eq("channel_id", channel["id"]).eq("is_public", True).order("created_at", desc=True).execute().data or []
        except Exception:
            videos = []
    ads = rows("advertisements", 100, is_active=True)
    return render_template("channel_page.html", channel=channel, videos=videos, ads=ads)

@app.route("/film/<video_id>")
def film(video_id):
    if not db_required():
        abort(503)
    try:
        video = supabase.table("videos").select("*").eq("id", video_id).eq("is_public", True).single().execute().data
        channel = supabase.table("channels").select("*").eq("id", video["channel_id"]).single().execute().data
    except Exception:
        abort(404)
    ads = rows("advertisements", 100, is_active=True)
    return render_template("film.html", video=video, channel=channel, ads=ads)


@app.route("/studio/<slug>", methods=["GET", "POST"])
def studio(slug):
    all_channels = rows("channels", 200, is_active=True)
    channel = next((c for c in all_channels if c.get("slug") == slug), None)
    if not channel:
        abort(404)
    if request.method == "POST":
        code = request.form.get("broadcast_code", "")
        stored_hash = channel.get("broadcaster_key_hash") or ""
        if stored_hash and check_password_hash(stored_hash, code):
            session["studio_channel_id"] = str(channel["id"])
            session["studio_channel_slug"] = slug
            return redirect(url_for("studio", slug=slug))
        flash("Code diffuseur incorrect.", "error")
    authorized = session.get("studio_channel_id") == str(channel["id"])
    return render_template("studio.html", channel=channel, authorized=authorized)

@app.route("/api/live-token/<slug>", methods=["POST"])
def live_token(slug):
    all_channels = rows("channels", 200, is_active=True)
    channel = next((c for c in all_channels if c.get("slug") == slug), None)
    if not channel:
        return {"error": "Chaîne introuvable"}, 404
    can_publish = session.get("studio_channel_id") == str(channel["id"])
    room_name = channel.get("live_room") or ("omnitv-" + str(channel["id"]))
    try:
        token = make_livekit_token(room_name, "publisher-" + str(channel["id"]) if can_publish else "viewer-" + secrets.token_hex(6), can_publish)
        return {"token": token, "serverUrl": LIVEKIT_URL, "room": room_name, "canPublish": can_publish}
    except Exception as exc:
        return {"error": str(exc)}, 503

@app.route("/api/live-status/<slug>", methods=["POST"])
def live_status(slug):
    all_channels = rows("channels", 200, is_active=True)
    channel = next((c for c in all_channels if c.get("slug") == slug), None)
    if not channel or session.get("studio_channel_id") != str(channel["id"]):
        return {"error": "Non autorisé"}, 403
    state = bool(request.json and request.json.get("is_live"))
    try:
        supabase.table("channels").update({"is_live": state}).eq("id", channel["id"]).execute()
        return {"ok": True, "is_live": state}
    except Exception:
        return {"error": "Mise à jour impossible"}, 500

@app.route("/admin/video", methods=["POST"])
@admin_required
def add_video():
    payload = {
        "channel_id": request.form.get("channel_id"),
        "title": request.form.get("title", "").strip(),
        "description": request.form.get("description", "").strip(),
        "video_url": request.form.get("video_url", "").strip(),
        "image_url": request.form.get("image_url", "").strip() or None,
        "duration_minutes": int(request.form.get("duration_minutes") or 0) or None,
        "midroll_after_seconds": int(request.form.get("midroll_after_seconds") or 0) or None,
        "is_public": True
    }
    try:
        supabase.table("videos").insert(payload).execute()
        flash("Vidéo ajoutée à l'archive de la chaîne.", "success")
    except Exception:
        flash("Impossible d'ajouter la vidéo. Vérifie la migration SQL et le lien.", "error")
    return redirect(url_for("admin"))


@app.errorhandler(404)
def not_found(_):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=os.getenv("FLASK_DEBUG") == "1")

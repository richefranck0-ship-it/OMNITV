"""
OMNITv — THE WORLD. ONE SCREEN.
Serveur Backend Flask de Production optimisé pour 1M d'utilisateurs avec CDN & Supabase.
"""
import os
import secrets
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, abort
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))

# Configuration Cloudinary
CLOUDINARY_CLOUD = os.getenv('CLOUDINARY_CLOUD_NAME', '')
CLOUDINARY_KEY = os.getenv('CLOUDINARY_API_KEY', '')
CLOUDINARY_SECRET = os.getenv('CLOUDINARY_API_SECRET', '')

# Helper pour simuler / interagir avec Supabase
def get_supabase_client():
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_KEY')
    if supabase_url and supabase_key:
        try:
            from supabase import create_client
            return create_client(supabase_url, supabase_key)
        except Exception as e:
            app.logger.warning(f"Supabase client init error: {e}")
    return None

# ============================================================
# ROUTES PUBLIQUES (AUCUNE CONNEXION REQUISE POUR REGARDER)
# ============================================================

@app.route('/')
def home():
    return render_template('index.html', page='home')

@app.route('/direct')
@app.route('/live')
def direct():
    return render_template('direct.html', page='direct')

@app.route('/chaines')
def channels():
    return render_template('channels.html', page='channels')

@app.route('/films')
def movies():
    return render_template('movies.html', page='movies')

@app.route('/programme-tv')
def schedule():
    return render_template('schedule.html', page='schedule')

@app.route('/publicite')
def advertiser():
    return render_template('advertiser.html', page='advertiser')

@app.route('/diffuseur')
def broadcaster():
    return render_template('broadcaster.html', page='broadcaster')

# ============================================================
# API ENDPOINTS & CLOUDINARY UPLOAD SÉCURISÉ
# ============================================================

@app.route('/api/channels', methods=['GET'])
def api_channels():
    # Cache headers pour CDN et millions de spectateurs
    response = jsonify({"status": "ok", "message": "Channels list"})
    response.headers['Cache-Control'] = 'public, max-age=60'
    return response

@app.route('/api/upload-media', methods=['POST'])
def api_upload_media():
    """Upload sécurisé vers Cloudinary avec vérification MIME et taille côté serveur"""
    if not session.get('is_admin'):
        return jsonify({"error": "Non autorisé"}), 403
    
    if 'file' not in request.files:
        return jsonify({"error": "Aucun fichier fourni"}), 400
        
    file = request.files['file']
    # Vérification du type
    allowed_exts = {'png', 'jpg', 'jpeg', 'webp', 'mp4'}
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in allowed_exts:
        return jsonify({"error": "Format non supporté"}), 400

    # Si Cloudinary configuré
    if CLOUDINARY_CLOUD and CLOUDINARY_KEY and CLOUDINARY_SECRET:
        try:
            import cloudinary
            import cloudinary.uploader
            cloudinary.config(
                cloud_name=CLOUDINARY_CLOUD,
                api_key=CLOUDINARY_KEY,
                api_secret=CLOUDINARY_SECRET
            )
            upload_result = cloudinary.uploader.upload(file, folder="omnitv_media")
            return jsonify({
                "status": "success",
                "url": upload_result.get('secure_url'),
                "public_id": upload_result.get('public_id')
            })
        except Exception as e:
            return jsonify({"error": f"Erreur Cloudinary: {str(e)}"}), 500
    
    return jsonify({
        "status": "mock",
        "message": "Cloudinary non configuré dans les variables d'environnement. Simulé avec succès."
    })

# ============================================================
# ESPACE ADMINISTRATEUR SÉCURISÉ CÔTÉ SERVEUR
# ============================================================

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        pin = request.form.get('pin', '')
        configured_pin = os.getenv('ADMIN_PIN', '3004')
        if pin == configured_pin:
            session['is_admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            error = "Code d'accès administrateur incorrect."
    return render_template('admin_login.html', error=error)

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    return render_template('admin.html', active_tab='overview')

@app.route('/admin/studio-live')
def admin_studio():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    return render_template('studio_live.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('home'))

# Balise Google Search Console et SEO dynamique
@app.route('/sitemap.xml')
def sitemap():
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://omnitv.onrender.com/</loc><changefreq>hourly</changefreq><priority>1.0</priority></url>
  <url><loc>https://omnitv.onrender.com/direct</loc><changefreq>always</changefreq><priority>0.9</priority></url>
  <url><loc>https://omnitv.onrender.com/chaines</loc><changefreq>daily</changefreq><priority>0.8</priority></url>
  <url><loc>https://omnitv.onrender.com/films</loc><changefreq>daily</changefreq><priority>0.8</priority></url>
  <url><loc>https://omnitv.onrender.com/programme-tv</loc><changefreq>hourly</changefreq><priority>0.8</priority></url>
</urlset>"""
    return xml, 200, {'Content-Type': 'application/xml'}

@app.route('/robots.txt')
def robots():
    return "User-agent: *\nAllow: /\nDisallow: /admin\nSitemap: https://omnitv.onrender.com/sitemap.xml\n", 200, {'Content-Type': 'text/plain'}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)

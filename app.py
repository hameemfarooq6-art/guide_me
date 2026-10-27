from flask import Flask, render_template, request, redirect, url_for, flash
from pathlib import Path
import sqlite3
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / 'travel_explorer.db'
UPLOAD_DIR = BASE_DIR / 'static' / 'uploads'
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}
app = Flask(__name__)
app.secret_key = 'change-this-for-a-real-deployment'

DESTINATIONS = [
    {'id': 1, 'slug': 'dal-lake', 'name': 'Dal Lake', 'location': 'Srinagar, Kashmir', 'category': 'Lake', 'description': 'A serene lake known for traditional houseboats, shikaras, floating markets, and mountain reflections.', 'image': 'dal-lake.svg', 'lat': 34.0837, 'lng': 74.8753, 'tip': 'Try an early-morning shikara ride and check local weather before heading out.'},
    {'id': 2, 'slug': 'gulmarg', 'name': 'Gulmarg', 'location': 'Baramulla, Kashmir', 'category': 'Mountain', 'description': 'A high-altitude getaway known for wide meadows, snowy winters, mountain views, and the gondola.', 'image': 'gulmarg.svg', 'lat': 34.0484, 'lng': 74.3805, 'tip': 'Weather can change quickly. Check gondola operations and road conditions before travel.'},
    {'id': 3, 'slug': 'pahalgam', 'name': 'Pahalgam', 'location': 'Anantnag, Kashmir', 'category': 'Valley', 'description': 'A green valley with the Lidder River, pine forests, mountain scenery, and walking routes.', 'image': 'pahalgam.svg', 'lat': 34.0161, 'lng': 75.3150, 'tip': 'Keep time for riverside walks and carry a light jacket.'},
    {'id': 4, 'slug': 'mughal-gardens', 'name': 'Mughal Gardens', 'location': 'Srinagar, Kashmir', 'category': 'Garden', 'description': 'Terraced gardens, flowing water channels, historic design, and views towards Dal Lake.', 'image': 'gardens.svg', 'lat': 34.0916, 'lng': 74.8800, 'tip': 'Spring and early summer are popular times for flowering gardens.'},
    {'id': 5, 'slug': 'sonamarg', 'name': 'Sonamarg', 'location': 'Ganderbal, Kashmir', 'category': 'Valley', 'description': 'A dramatic mountain valley with alpine scenery, rivers, and seasonal excursions.', 'image': 'sonamarg.svg', 'lat': 34.3042, 'lng': 75.2931, 'tip': 'Check seasonal road access and local advisories before planning a trip.'},
    {'id': 6, 'slug': 'yusmarg', 'name': 'Yusmarg', 'location': 'Budgam, Kashmir', 'category': 'Valley', 'description': 'A peaceful meadow surrounded by pine-covered hills, suited to slow days in nature.', 'image': 'yusmarg.svg', 'lat': 33.8350, 'lng': 74.6620, 'tip': 'Pack water and snacks and check return transport arrangements ahead of time.'},
]


def connect_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with connect_db() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            destination_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
            comment TEXT NOT NULL,
            photo_filename TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )''')
        count = conn.execute('SELECT COUNT(*) FROM reviews').fetchone()[0]
        if count == 0:
            conn.executemany('INSERT INTO reviews (destination_id,name,rating,comment) VALUES (?,?,?,?)', [
                (1, 'Ayesha K.', 5, 'The lake was peaceful in the morning and the mountain reflections were beautiful.'),
                (2, 'Rahul M.', 4, 'Amazing mountain views and fresh air. Check the weather before visiting.'),
                (3, 'Sana R.', 5, 'A beautiful valley for nature lovers. The river and green surroundings were memorable.'),
            ])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def destination_data(search='', category='All'):
    conn = connect_db()
    data = []
    for destination in DESTINATIONS:
        if search and search.lower() not in (destination['name'] + ' ' + destination['location'] + ' ' + destination['description']).lower():
            continue
        if category not in ('All', '') and destination['category'] != category:
            continue
        row = conn.execute('SELECT COUNT(*) AS total, AVG(rating) AS avg_rating FROM reviews WHERE destination_id=?', (destination['id'],)).fetchone()
        item = dict(destination)
        item['review_count'] = row['total']
        item['rating'] = round(row['avg_rating'], 1) if row['avg_rating'] is not None else 0
        data.append(item)
    conn.close()
    return data


@app.route('/')
def home():
    search = request.args.get('q', '').strip()[:100]
    category = request.args.get('category', 'All')
    if category not in ('All', 'Lake', 'Mountain', 'Valley', 'Garden'):
        category = 'All'
    destinations = destination_data(search, category)
    conn = connect_db()
    rows = conn.execute('SELECT * FROM reviews ORDER BY id DESC LIMIT 6').fetchall()
    conn.close()
    place_by_id = {d['id']: d for d in DESTINATIONS}
    recent_reviews = []
    for row in rows:
        item = dict(row)
        place = place_by_id.get(item['destination_id'], {})
        item['destination_name'] = place.get('name', 'Kashmir')
        item['destination_slug'] = place.get('slug', 'dal-lake')
        recent_reviews.append(item)
    return render_template('index.html', destinations=destinations, recent_reviews=recent_reviews, q=search, category=category, categories=['All','Lake','Mountain','Valley','Garden'])


@app.route('/destination/<slug>')
def destination_detail(slug):
    destination = next((d for d in DESTINATIONS if d['slug'] == slug), None)
    if not destination:
        return render_template('404.html'), 404
    conn = connect_db()
    reviews = conn.execute('SELECT * FROM reviews WHERE destination_id=? ORDER BY id DESC', (destination['id'],)).fetchall()
    stats = conn.execute('SELECT COUNT(*) AS total, AVG(rating) AS avg_rating FROM reviews WHERE destination_id=?', (destination['id'],)).fetchone()
    conn.close()
    destination = dict(destination)
    destination['review_count'] = stats['total']
    destination['rating'] = round(stats['avg_rating'], 1) if stats['avg_rating'] is not None else 0
    return render_template('destination.html', destination=destination, reviews=reviews)


@app.route('/review', methods=['POST'])
def add_review():
    try:
        destination_id = int(request.form.get('destination_id', '0'))
        rating = int(request.form.get('rating', '0'))
    except ValueError:
        flash('Please choose a destination and a valid rating.', 'error')
        return redirect(url_for('home'))
    destination = next((d for d in DESTINATIONS if d['id'] == destination_id), None)
    name = request.form.get('name', '').strip()[:45]
    comment = request.form.get('comment', '').strip()[:1000]
    if not destination or not name or len(comment) < 8 or rating not in range(1, 6):
        flash('Please complete every required field. A review must be at least 8 characters.', 'error')
        return redirect(url_for('home'))
    filename = None
    photo = request.files.get('photo')
    if photo and photo.filename:
        if not allowed_file(photo.filename):
            flash('Photo must be PNG, JPG, JPEG, WEBP, or GIF.', 'error')
            return redirect(url_for('destination_detail', slug=destination['slug']))
        if len(photo.read()) > 2 * 1024 * 1024:
            flash('Please choose a photo smaller than 2 MB.', 'error')
            return redirect(url_for('destination_detail', slug=destination['slug']))
        photo.seek(0)
        filename = secure_filename(f"{destination['slug']}_{photo.filename}")
        photo.save(UPLOAD_DIR / filename)
    with connect_db() as conn:
        conn.execute('INSERT INTO reviews (destination_id,name,rating,comment,photo_filename) VALUES (?,?,?,?,?)', (destination_id, name, rating, comment, filename))
    flash('Thanks! Your review has been saved.', 'success')
    return redirect(url_for('destination_detail', slug=destination['slug']))


@app.errorhandler(413)
def too_large(_error):
    flash('The uploaded file is too large.', 'error')
    return redirect(url_for('home'))

app.config['MAX_CONTENT_LENGTH'] = 3 * 1024 * 1024
init_db()

if __name__ == '__main__':
    app.run(debug=True, port=5000)

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail, Message
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, validators
import math

ADMIN_EMAIL = "admin@gmail.com"
ADMIN_PASSWORD = "admin123"

app = Flask(__name__, static_folder='Templates/Static')
app.secret_key = 'your_secret_key'

# Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'kaivalyapatil.rns@gmail.com'  # Your Gmail
app.config['MAIL_PASSWORD'] = 'zhmf ipoa pocq vyuf'  # Gmail App Password
app.config['MAIL_DEFAULT_SENDER'] = 'kaivalyapatil.rns@gmail.com'
mail = Mail(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///medicine_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# ------------------ Models ------------------

class Owner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    stores = db.relationship('Store', backref='owner', cascade="all, delete", lazy=True)


class Store(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    owner_id = db.Column(db.Integer, db.ForeignKey('owner.id'), nullable=False)
    medicines = db.relationship('Medicine', backref='store', cascade="all, delete", lazy=True)


class Medicine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'), nullable=False)


class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200))
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ------------------ Routes ------------------


@app.route('/', methods=['GET', 'POST'])
def home():
    results = []
    if request.method == 'POST':
        search_query = request.form['search'].strip().lower()
        user_lat = request.form.get('latitude')
        user_lon = request.form.get('longitude')

        if not user_lat or not user_lon:
            flash("Location not shared. Cannot filter nearby stores.", "warning")
            return redirect(url_for('home'))

        user_lat = float(user_lat)
        user_lon = float(user_lon)

        # Search medicines
        matches = Medicine.query.filter(Medicine.name.ilike(f"%{search_query}%")).all()

        for med in matches:
            store = Store.query.get(med.store_id)
            if store.latitude and store.longitude:
                distance = haversine(user_lat, user_lon, store.latitude, store.longitude)
                if distance <= 1.0:  # within 1 km
                    results.append({
                        'medicine': med.name,
                        'quantity': med.quantity,
                        'store': store.name,
                        'phone': store.phone,
                        'location': store.location,
                        'latitude': store.latitude,
                        'longitude': store.longitude,
                        'distance': round(distance, 2)
                    })

    return render_template('home.html', results=results)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        # Save to database
        new_message = ContactMessage(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        db.session.add(new_message)
        db.session.commit()

        # Send email notification
        msg = Message(
            subject=f"New Contact Message: {subject}",
            recipients=[ADMIN_EMAIL],  # Using your existing admin email
            body=f"""
            From: {name} ({email})
            Subject: {subject}

            Message:
            {message}
            """
        )
        mail.send(msg)

        flash('Your message has been sent successfully!', 'success')
        return redirect(url_for('contact'))

    return render_template('contact.html')


@app.route('/privacy')
def privacy():
    return render_template('privacy.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        if Owner.query.filter_by(email=email).first():
            flash('Email already exists. Try logging in.', 'warning')
            return redirect(url_for('login'))

        new_owner = Owner(name=name, email=email, password=password)
        db.session.add(new_owner)
        db.session.commit()
        flash('Signup successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        owner = Owner.query.filter_by(email=email, password=password).first()
        if owner:
            session['owner_id'] = owner.id
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'owner_id' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('login'))
    # ... any other logic for dashboard that might have been here
    owner = Owner.query.get(session['owner_id'])
    return render_template('dashboard.html', owner=owner)


@app.route('/logout')
def logout():
    session.pop('owner_id', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('home'))


# ------------------ Store Management ------------------

@app.route('/add_store', methods=['GET', 'POST'])
def add_store():
    if 'owner_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['store_name']
        phone = request.form['phone']
        location = request.form['location']
        lat = request.form['latitude']
        lon = request.form['longitude']

        store = Store(
            name=name,
            phone=phone,
            location=location,
            latitude=lat,
            longitude=lon,
            owner_id=session['owner_id']
        )
        db.session.add(store)
        db.session.commit()
        flash('Store added successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('add_store.html')


@app.route('/edit_store/<int:store_id>', methods=['GET', 'POST'])
def edit_store(store_id):
    if 'owner_id' not in session:
        flash('Please log in.', 'warning')
        return redirect(url_for('login'))

    store = Store.query.get_or_404(store_id)

    if store.owner_id != session['owner_id']:
        flash("Unauthorized access.", "danger")
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        store.name = request.form['store_name']
        store.phone = request.form['phone']
        store.location = request.form['location']
        store.latitude = float(request.form['latitude'])
        store.longitude = float(request.form['longitude'])
        db.session.commit()
        flash("Store updated successfully.", "success")
        return redirect(url_for('dashboard'))

    return render_template('edit_store.html', store=store)


@app.route('/delete_store/<int:store_id>', methods=['POST'])
def delete_store(store_id):
    if 'owner_id' not in session:
        flash('Please log in.', 'warning')
        return redirect(url_for('login'))

    store = Store.query.get_or_404(store_id)

    if store.owner_id != session['owner_id']:
        flash("Unauthorized access.", "danger")
        return redirect(url_for('dashboard'))

    db.session.delete(store)
    db.session.commit()
    flash("Store deleted.", "info")
    return redirect(url_for('dashboard'))


# ------------------ Medicine Management ------------------

@app.route('/add_medicine/<int:store_id>', methods=['POST'])
def add_medicine(store_id):
    if 'owner_id' not in session:
        return redirect(url_for('login'))

    store = Store.query.get_or_404(store_id)
    if store.owner_id != session['owner_id']:
        flash("Unauthorized", "danger")
        return redirect(url_for('dashboard'))

    name = request.form['name']
    quantity = request.form['quantity']

    med = Medicine(name=name, quantity=quantity, store_id=store.id)
    db.session.add(med)
    db.session.commit()
    flash('Medicine added successfully!', 'success')
    return redirect(url_for('dashboard'))


@app.route('/edit_medicine/<int:med_id>', methods=['GET', 'POST'])
def edit_medicine(med_id):
    if 'owner_id' not in session:
        return redirect(url_for('login'))

    med = Medicine.query.get_or_404(med_id)
    if med.store.owner_id != session['owner_id']:
        flash('Unauthorized', 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        med.quantity = request.form['quantity']
        db.session.commit()
        flash('Medicine updated!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('edit_medicine.html', medicine=med)


@app.route('/delete_medicine/<int:med_id>', methods=['POST'])
def delete_medicine(med_id):
    if 'owner_id' not in session:
        return redirect(url_for('login'))

    med = Medicine.query.get_or_404(med_id)
    if med.store.owner_id != session['owner_id']:
        flash('Unauthorized', 'danger')
        return redirect(url_for('dashboard'))

    db.session.delete(med)
    db.session.commit()
    flash('Medicine deleted!', 'info')
    return redirect(url_for('dashboard'))


@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            session['admin'] = True
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials.', 'danger')
    return render_template('admin_login.html')


@app.route('/admin-dashboard')
def admin_dashboard():
    if 'admin' not in session:
        flash('Admin access only.', 'danger')
        return redirect(url_for('admin_login'))

    owners = Owner.query.all()
    stores = Store.query.all()
    medicines = Medicine.query.all()
    contact_messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).limit(5).all()
    return render_template('admin_dashboard.html', owners=owners, stores=stores, medicines=medicines,
                           contact_messages=contact_messages)


@app.route('/admin/messages')
def all_messages():
    if 'admin' not in session:
        flash('Admin access only.', 'danger')
        return redirect(url_for('admin_login'))

    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template('admin_messages.html', messages=messages)


@app.route('/admin/delete-message/<int:message_id>')
def delete_message(message_id):
    if 'admin' not in session:
        flash('Admin access only.', 'danger')
        return redirect(url_for('admin_login'))

    message = ContactMessage.query.get_or_404(message_id)
    db.session.delete(message)
    db.session.commit()
    flash('Message deleted successfully.', 'success')
    return redirect(request.referrer or url_for('admin_dashboard'))  # Uses request.referrer for flexible redirect


@app.route('/admin-logout')
def admin_logout():
    session.pop('admin', None)
    flash('Admin logged out.', 'info')
    return redirect(url_for('home'))


@app.route('/delete-owner/<int:owner_id>', methods=['POST'])
def delete_owner():
    if 'admin_logged_in' not in session:  # Note: this session key seems inconsistent ('admin' vs 'admin_logged_in')
        flash('Admin login required', 'danger')
        return redirect(url_for('admin_login'))

    owner_id = request.view_args['owner_id']  # Correct way to get route argument in this context
    owner = Owner.query.get_or_404(owner_id)

    db.session.delete(owner)
    db.session.commit()
    flash(f'Owner {owner.name} and all related data deleted.', 'info')
    return redirect(url_for('admin_dashboard'))


def haversine(lat1, lon1, lat2, lon2):
    # Convert degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    return 6371 * c  # Radius of earth in kilometers


@app.after_request
def add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


# ------------------ Init DB ------------------

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)

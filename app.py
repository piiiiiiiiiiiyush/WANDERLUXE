from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'

# Database initialization
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        phone TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Packages table
    c.execute('''CREATE TABLE IF NOT EXISTS packages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        destination TEXT NOT NULL,
        duration INTEGER NOT NULL,
        price REAL NOT NULL,
        description TEXT,
        image_url TEXT,
        highlights TEXT,
        itinerary TEXT
    )''')
    
    # Bookings table
    c.execute('''CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        package_id INTEGER NOT NULL,
        booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        travel_date DATE NOT NULL,
        travelers_count INTEGER NOT NULL,
        total_amount REAL NOT NULL,
        status TEXT DEFAULT 'pending',
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (package_id) REFERENCES packages(id)
    )''')
    
    # Reviews table
    c.execute('''CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        package_id INTEGER NOT NULL,
        rating INTEGER NOT NULL,
        comment TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (package_id) REFERENCES packages(id)
    )''')
    
    conn.commit()
    
    # Insert sample packages if table is empty
    c.execute('SELECT COUNT(*) FROM packages')
    if c.fetchone()[0] == 0:
        insert_sample_packages(conn)
    
    conn.close()

def insert_sample_packages(conn):
    c = conn.cursor()
    packages = [
        ('Varanasi Spiritual Tour', 'Spiritual', 'Varanasi', 3, 8999, 
         'Experience the spiritual essence of Kashi with Ganga Aarti and ancient temples',
         'Banarrs.jpg', 
         'Ganga Aarti|Kashi Vishwanath|Sarnath|Boat Ride',
         'Day 1: Arrival and Ganga Aarti\nDay 2: Temple visits and Sarnath\nDay 3: Departure'),
        
        ('Ayodhya Darshan', 'Spiritual', 'Ayodhya', 2, 6499,
         'Visit the holy city of Lord Ram - Ram Mandir and Hanuman Garhi',
         'Aodhya.jpg',
         'Ram Mandir|Hanuman Garhi|Saryu Aarti',
         'Day 1: Ram Mandir and temples\nDay 2: Saryu Aarti and departure'),
        
        ('Char Dham Yatra', 'Spiritual', 'Uttarakhand', 10, 45999,
         'Complete pilgrimage to Kedarnath, Badrinath, Gangotri, and Yamunotri',
         'Char dham.jpg', 'Kedarnath|Badrinath|Gangotri|Yamunotri',
         '10 days complete itinerary covering all four dhams'),
        
        ('Mathura Vrindavan Spiritual', 'Spiritual', 'Mathura', 3, 9999,
         'Krishna circuit with Janmabhoomi and Banke Bihari temple',
         'Mathura.jpeg', 'Krishna Janmabhoomi|Banke Bihari|Prem Mandir',
         'Day 1-3: Complete Krishna circuit tour'),
        
        ('Amritsar Golden Temple', 'Spiritual', 'Amritsar', 3, 11999,
         'Visit the Golden Temple and Wagah Border',
         'Amritsar (2).jpg', 'Golden Temple|Wagah Border|Jallianwala Bagh',
         'Day 1-3: Spiritual and historical tour'),
        
        ('Manali Honeymoon Special', 'Hill Station', 'Manali', 5, 18999,
         'Romantic getaway with snow activities and beautiful valleys',
         'Manalii.jpg', 'Rohtang Pass|Solang Valley|Hadimba Temple|Mall Road',
         'Day 1-5: Complete Manali honeymoon package'),
        
        ('Shimla Manali Combo', 'Hill Station', 'Shimla-Manali', 6, 22999,
         'Best of both hill stations in one package',
         'manali_shimla.jpg', 'Mall Road|Kufri|Solang|Rohtang',
         'Day 1-6: Shimla and Manali tour'),
        
        ('Goa Beach Paradise', 'Beach', 'Goa', 4, 12999,
         'Beach fun with water sports and nightlife',
         'goa.jpg', 'North Goa Beaches|Water Sports|Nightlife|Churches',
         'Day 1-4: Complete Goa beach experience'),
        
        ('Andaman Islands', 'Beach', 'Andaman', 6, 35999,
         'Island paradise with scuba diving and pristine beaches',
         'island.jpg', 'Havelock|Neil Island|Scuba Diving|Cellular Jail',
         'Day 1-6: Island hopping and water activities'),
        
        ('Rajasthan Royal Tour', 'Cultural', 'Rajasthan', 7, 28999,
         'Experience the royal heritage of Rajasthan',
         'rajasthan.jpg', 'Jaipur|Udaipur|Jaisalmer|Desert Safari',
         'Day 1-7: Complete Rajasthan circuit'),
        
        ('Agra Taj Mahal Special', 'Cultural', 'Agra', 2, 7999,
         'Taj Mahal and Agra Fort guided tour',
         'agra.jpg', 'Taj Mahal|Agra Fort|Fatehpur Sikri',
         'Day 1-2: Complete Agra sightseeing'),
        
        ('Kerala Backwaters', 'Beach', 'Kerala', 5, 24999,
         'Houseboat experience with backwaters and beaches',
         'kerala.jpg', 'Houseboat|Alleppey|Munnar|Kovalam Beach',
         'Day 1-5: Kerala complete tour')
    ]
    
    c.executemany('''INSERT INTO packages 
        (name, category, destination, duration, price, description, image_url, highlights, itinerary)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', packages)
    conn.commit()

# Routes
@app.route('/')
def index():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM packages LIMIT 8')
    packages = c.fetchall()
    conn.close()
    return render_template('index.html', packages=packages)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        phone = request.form.get('phone', '')
        
        hashed_password = generate_password_hash(password)
        
        try:
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute('INSERT INTO users (name, email, password, phone) VALUES (?, ?, ?, ?)',
                     (name, email, hashed_password, phone))
            conn.commit()
            conn.close()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already exists!', 'error')
            return redirect(url_for('signup'))
    
    return render_template('signup.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        login_type = request.form.get('login_type', 'customer')  # NEW
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = c.fetchone()
        conn.close()
        
        if user and check_password_hash(user[3], password):
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            session['user_email'] = user[2]
            
            # NEW: Admin vs Customer Login
            if login_type == 'admin':
                # Check if admin email
                if user[2] == 'piyushtripaathi4@gmail.com':
                    flash('Admin login successful!', 'success')
                    return redirect(url_for('admin_bookings'))  # Direct admin panel
                else:
                    flash('Access Denied! Not an admin account.', 'error')
                    session.clear()
                    return redirect(url_for('login'))
            else:
                # Customer login
                flash('Login successful!', 'success')
                return redirect(url_for('index'))
        else:
            flash('Invalid email or password!', 'error')
            return redirect(url_for('login'))
    
    return render_template('login.html')
@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/packages')
def packages():
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    query = 'SELECT * FROM packages WHERE 1=1'
    params = []
    
    if category:
        query += ' AND category = ?'
        params.append(category)
    
    if search:
        query += ' AND (name LIKE ? OR destination LIKE ?)'
        params.extend([f'%{search}%', f'%{search}%'])
    
    c.execute(query, params)
    packages = c.fetchall()
    conn.close()
    
    return render_template('packages.html', packages=packages)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/package/<int:package_id>')
def package_details(package_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM packages WHERE id = ?', (package_id,))
    package = c.fetchone()
    
    c.execute('''SELECT reviews.*, users.name FROM reviews 
                 JOIN users ON reviews.user_id = users.id 
                 WHERE package_id = ?''', (package_id,))
    reviews = c.fetchall()
    conn.close()
    
    return render_template('package_details.html', package=package, reviews=reviews)

@app.route('/book/<int:package_id>', methods=['GET', 'POST'])
def book_package(package_id):
    if 'user_id' not in session:
        flash('Please login to book a package!', 'error')
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM packages WHERE id = ?', (package_id,))
    package = c.fetchone()
    
    if not package:
        flash('Package not found!', 'error')
        conn.close()
        return redirect(url_for('packages'))
    
    if request.method == 'POST':
        travel_date = request.form.get('travel_date')
        travelers_count = int(request.form.get('travelers_count', 1))
        
        total_amount = package[5] * travelers_count
        
        c.execute('''INSERT INTO bookings 
                     (user_id, package_id, travel_date, travelers_count, total_amount)
                     VALUES (?, ?, ?, ?, ?)''',
                  (session['user_id'], package_id, travel_date, travelers_count, total_amount))
        conn.commit()
        conn.close()
        
        flash('Booking successful!', 'success')
        return redirect(url_for('dashboard'))
    
    conn.close()
    return render_template('booking.html', package=package)

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please login first!', 'error')
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''SELECT bookings.*, packages.name, packages.destination 
                 FROM bookings 
                 JOIN packages ON bookings.package_id = packages.id
                 WHERE user_id = ? ORDER BY booking_date DESC''', (session['user_id'],))
    bookings = c.fetchall()
    conn.close()
    
    return render_template('dashboard.html', bookings=bookings)

@app.route('/admin/bookings')
def admin_bookings():
    if 'user_id' not in session:
        flash('Please login first!', 'error')
        return redirect(url_for('login'))
    
    # ADMIN CHECK - Sirf ye email admin hai
    if session.get('user_email') != 'piyushtripaathi4@gmail.com':
        flash('Access Denied! Admin only.', 'error')
        return redirect(url_for('index'))
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''SELECT bookings.*, packages.name, packages.destination, users.name as user_name, users.email
                 FROM bookings 
                 JOIN packages ON bookings.package_id = packages.id
                 JOIN users ON bookings.user_id = users.id
                 ORDER BY booking_date DESC''')
    all_bookings = c.fetchall()
    conn.close()
    
    return render_template('admin_bookings.html', bookings=all_bookings)

@app.route('/admin/confirm/<int:booking_id>')
def confirm_booking(booking_id):
    if 'user_id' not in session:
        flash('Please login first!', 'error')
        return redirect(url_for('login'))
    
    # ADMIN CHECK
    if session.get('user_email') != 'piyushtripaathi4@gmail.com':
        flash('Access Denied! Admin only.', 'error')
        return redirect(url_for('index'))
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('UPDATE bookings SET status = ? WHERE id = ?', ('confirmed', booking_id))
    conn.commit()
    conn.close()
    
    flash('Booking confirmed successfully!', 'success')
    return redirect(url_for('admin_bookings'))

@app.route('/admin/cancel/<int:booking_id>')
def cancel_booking(booking_id):
    if 'user_id' not in session:
        flash('Please login first!', 'error')
        return redirect(url_for('login'))
    
    # ADMIN CHECK
    if session.get('user_email') != 'piyushtripaathi4@gmail.com':
        flash('Access Denied! Admin only.', 'error')
        return redirect(url_for('index'))
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('UPDATE bookings SET status = ? WHERE id = ?', ('cancelled', booking_id))
    conn.commit()
    conn.close()
    
    flash('Booking cancelled!', 'error')
    return redirect(url_for('admin_bookings'))

# ADMIN ROUTES - Booking Management


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

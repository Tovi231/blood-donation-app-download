from flask import Flask, request, jsonify, session
from flask_cors import CORS
import sqlite3
import hashlib
import re
from datetime import datetime
import time
from functools import wraps

app = Flask(__name__)
CORS(app, supports_credentials=True)  # Enable CORS with credentials
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key

# Rate limiting
login_attempts = {}

def rate_limit(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        ip = request.remote_addr
        if ip in login_attempts:
            if time.time() - login_attempts[ip]['time'] < 300:  # 5 minutes
                if login_attempts[ip]['count'] >= 5:
                    return jsonify({'error': 'Too many login attempts. Please try again later.'}), 429
                login_attempts[ip]['count'] += 1
            else:
                login_attempts[ip] = {'count': 1, 'time': time.time()}
        else:
            login_attempts[ip] = {'count': 1, 'time': time.time()}
        return f(*args, **kwargs)
    return decorated_function

def get_db_connection():
    """Create a database connection with error handling"""
    try:
        conn = sqlite3.connect('users.db')
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

def create_db():
    """Creates the users table if it does not exist"""
    conn = get_db_connection()
    if conn is None:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            full_name TEXT NOT NULL,
                            phone TEXT UNIQUE NOT NULL,
                            dob TEXT NOT NULL,
                            username TEXT UNIQUE NOT NULL,
                            password TEXT NOT NULL,
                            email TEXT UNIQUE,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                          )''')
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Database creation error: {e}")
        return False
    finally:
        conn.close()

def validate_phone(phone):
    """Validate phone number format"""
    pattern = r'^\+?1?\d{9,15}$'
    return bool(re.match(pattern, phone))

def validate_email(email):
    """Validate email format"""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

def validate_username(username):
    """Validate username format"""
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    return bool(re.match(pattern, username))

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    return True

def validate_dob(dob):
    """Validate date of birth"""
    try:
        dob_date = datetime.strptime(dob, '%Y-%m-%d')
        if dob_date > datetime.now():
            return False
        age = (datetime.now() - dob_date).days / 365.25
        return 18 <= age <= 100
    except ValueError:
        return False

def hash_password(password):
    """Hashes the password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        full_name = data.get('full_name', '').strip()
        phone = data.get('phone', '').strip()
        dob = data.get('dob', '').strip()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        email = data.get('email', '').strip()
        
        # Validate all required fields
        if not all([full_name, phone, dob, username, password, email]):
            return jsonify({'error': 'All fields are required'}), 400
        
        # Validate input formats
        if not validate_phone(phone):
            return jsonify({'error': 'Invalid phone number format'}), 400
        
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        if not validate_username(username):
            return jsonify({'error': 'Username must be 3-20 characters long and contain only letters, numbers, and underscores'}), 400
        
        if not validate_password(password):
            return jsonify({'error': 'Password must be at least 8 characters long and contain uppercase, lowercase, and numbers'}), 400
        
        if not validate_dob(dob):
            return jsonify({'error': 'Invalid date of birth. You must be at least 18 years old'}), 400
        
        hashed_password = hash_password(password)
        
        conn = get_db_connection()
        if conn is None:
            return jsonify({'error': 'Database connection error'}), 500
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (full_name, phone, dob, username, password, email)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (full_name, phone, dob, username, hashed_password, email))
            conn.commit()
            return jsonify({'message': 'User registered successfully'}), 201
        except sqlite3.IntegrityError as e:
            if 'username' in str(e):
                return jsonify({'error': 'Username already exists'}), 400
            elif 'phone' in str(e):
                return jsonify({'error': 'Phone number already registered'}), 400
            elif 'email' in str(e):
                return jsonify({'error': 'Email already registered'}), 400
            return jsonify({'error': 'Registration failed'}), 400
        finally:
            conn.close()
    except Exception as e:
        return jsonify({'error': 'Server error occurred'}), 500

@app.route('/login', methods=['POST'])
@rate_limit
def login():
    try:
        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        hashed_password = hash_password(password)
        
        conn = get_db_connection()
        if conn is None:
            return jsonify({'error': 'Database connection error'}), 500
        
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username=? AND password=?", 
                         (username, hashed_password))
            user = cursor.fetchone()
            
            if user:
                # Create session
                session['user_id'] = user['id']
                session['username'] = user['username']
                
                return jsonify({
                    'message': 'Login successful',
                    'user': {
                        'id': user['id'],
                        'full_name': user['full_name'],
                        'username': user['username'],
                        'email': user['email']
                    }
                }), 200
            else:
                return jsonify({'error': 'Invalid username or password'}), 401
        finally:
            conn.close()
    except Exception as e:
        return jsonify({'error': 'Server error occurred'}), 500

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

if __name__ == '__main__':
    if create_db():
        app.run(debug=True, port=5000)
    else:
        print("Failed to initialize database")

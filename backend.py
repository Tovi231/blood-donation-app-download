from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import hashlib

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def create_db():
    """Creates the users table if it does not exist"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        full_name TEXT NOT NULL,
                        phone TEXT UNIQUE NOT NULL,
                        dob TEXT NOT NULL,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL
                      )''')
    conn.commit()
    conn.close()

create_db()

def hash_password(password):
    """Hashes the password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    full_name = data.get('full_name')
    phone = data.get('phone')
    dob = data.get('dob')
    username = data.get('username')
    password = data.get('password')
    
    if not (full_name and phone and dob and username and password):
        return jsonify({'error': 'All fields are required'}), 400
    
    hashed_password = hash_password(password)
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (full_name, phone, dob, username, password) VALUES (?, ?, ?, ?, ?)", 
                       (full_name, phone, dob, username, hashed_password))
        conn.commit()
        conn.close()
        return jsonify({'message': 'User registered successfully'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Username or Phone already exists'}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not (username and password):
        return jsonify({'error': 'Username and password are required'}), 400
    
    hashed_password = hash_password(password)
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed_password))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user[0],
                'full_name': user[1],
                'username': user[4]
            }
        }), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401 

if __name__ == '__main__':
    app.run(debug=True, port=5000)

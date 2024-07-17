from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from getpass import getpass
import hashlib

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Connect to the SQLite3 database
def connect_db():
    return sqlite3.connect('users.db')

# Create the users table
def create_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Register a new user
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash("Passwords do not match!")
            return redirect(url_for('register'))

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        conn = connect_db()
        cursor = conn.cursor()
        
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            flash("User registered successfully!")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Username already exists!")
            return redirect(url_for('register'))
        finally:
            conn.close()
    return render_template('register.html')

# Login a user
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password))
        user = cursor.fetchone()
        
        if user:
            session['username'] = username
            flash("Login successful!")
            return redirect(url_for('welcome'))
        else:
            flash("Invalid username or password!")
            return redirect(url_for('login'))
    return render_template('login.html')

# Welcome page after login
@app.route('/welcome')
def welcome():
    if 'username' in session:
        return f"Welcome {session['username']}!"
    else:
        return redirect(url_for('login'))

# Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("You have been logged out!")
    return redirect(url_for('login'))

if __name__ == "__main__":
    create_table()
    app.run(debug=True)

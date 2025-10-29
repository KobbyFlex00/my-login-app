import sqlite3
import hashlib
import os # Import the os module
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

# --- App Configuration ---
app = Flask(__name__)
app.secret_key = "829251f6c5da74ed0e9fcf0f639a3bc0" 

# --- Database Path Configuration ---
# This finds the directory the app.py file is in
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# This creates the full path for the database file
DATABASE_PATH = os.path.join(BASE_DIR, "users.db")

# --- Helper Function: Initialize Database ---
def init_db():
    """Creates the users.db and users1 table if they don't exist."""
    # Use the absolute path
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users1(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()

# --- Route: Login Page (and root) ---
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Use the absolute path
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT username, role, password FROM users1 WHERE username=?", (username,))
        user_data = cursor.fetchone()
        conn.close()

        if user_data and check_password_hash(user_data[2], password):
            user = (user_data[0], user_data[1])
        else:
            user = None

        if user:
            session['username'] = user[0]
            session['role'] = user[1]
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

# --- Route: Signup Page ---
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        role = request.form['role']

        if not username or not password or not confirm_password or not role:
            flash('All fields are required!', 'warning')
            return redirect(url_for('signup'))

        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('signup'))
        
        hashed_pwd = generate_password_hash(password)
        
        try:
            # Use the absolute path
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users1 (username, password, role) VALUES (?, ?, ?)",
                           (username, hashed_pwd, role))
            conn.commit()
            conn.close()
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists.', 'danger')
            return redirect(url_for('signup'))
        # This will catch the "no such table" error just in case
        except sqlite3.OperationalError as e:
            flash(f"Database error: {e}. Please contact admin.", 'danger')
            return redirect(url_for('signup'))


    return render_template('signup.html')

# --- Route: Dashboard (Protected) ---
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash('You must be logged in to view this page.', 'warning')
        return redirect(url_for('login'))
    
    return render_template('dashboard.html')

# --- Route: View Users (Admin Only) ---
@app.route('/view_users')
def view_users():
    if 'username' not in session:
        flash('You must be logged in to view this page.', 'warning')
        return redirect(url_for('login'))
    if session['role'] != 'Admin':
        flash('You do not have permission to view this page.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Use the absolute path
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role FROM users1")
    users = cursor.fetchall()
    conn.close()
    
    return render_template('view_users.html', users=users)

# --- Route: Change Password (Logged in users) ---
@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'username' not in session:
        flash('You must be logged in to view this page.', 'warning')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirm_new_password = request.form['confirm_new_password']
        
        if not old_password or not new_password or not confirm_new_password:
            flash('All fields are required!', 'warning')
            return redirect(url_for('change_password'))
        
        if new_password != confirm_new_password:
            flash('New passwords do not match!', 'danger')
            return redirect(url_for('change_password'))
            
        username = session['username']
        # Use the absolute path
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT password FROM users1 WHERE username=?", (username,))
        stored_hash = cursor.fetchone()[0]
        
        if not check_password_hash(stored_hash, old_password):
            flash('Old password is incorrect.', 'danger')
            conn.close()
            return redirect(url_for('change_password'))
        
        hashed_new_pwd = generate_password_hash(new_password)
        
        # --- THIS IS THE FIX ---
        # The variable is now 'hashed_new_pwd' (no stray underscore)
        cursor.execute("UPDATE users1 SET password=? WHERE username=?", (hashed_new_pwd, username))
        # --- END FIX ---
        
        conn.commit()
        conn.close()
        
        flash('Password updated successfully!', 'success')
        return redirect(url_for('dashboard'))
        
    return render_template('change_password.html')

# --- Route: Logout ---
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

# --- Main execution ---
if __name__ == '__main__':
    init_db()  # This will now create the DB in the correct local folder
    app.run(debug=False) # Debug mode is OFF for deployment
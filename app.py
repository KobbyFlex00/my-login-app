import sqlite3
import hashlib
from flask import Flask, render_template, request, redirect, url_for, session, flash
# Import new libraries for better password hashing
from werkzeug.security import generate_password_hash, check_password_hash

# --- App Configuration ---
app = Flask(__name__)
# 1. NEW Random Secret Key for security
app.secret_key = "829251f6c5da74ed0e9fcf0f639a3bc0" 

# --- Helper Function: Initialize Database ---
def init_db():
    """Creates the users.db and users1 table if they don't exist."""
    conn = sqlite3.connect('users.db')
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

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        # 2. UPDATED Login Logic: Fetch user first, then check hash
        cursor.execute("SELECT username, role, password FROM users1 WHERE username=?", (username,))
        user_data = cursor.fetchone()
        conn.close()

        # Check hash in Python
        if user_data and check_password_hash(user_data[2], password): # user_data[2] is the stored hash
            user = (user_data[0], user_data[1]) # Create the 'user' tuple
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
        
        # 3. UPDATED Hashing: Use generate_password_hash
        hashed_pwd = generate_password_hash(password)
        
        try:
            conn = sqlite3.connect('users.db')
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
    
    conn = sqlite3.connect('users.db')
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
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        # 4. UPDATED Check: Fetch hash and use check_password_hash
        cursor.execute("SELECT password FROM users1 WHERE username=?", (username,))
        stored_hash = cursor.fetchone()[0]
        
        if not check_password_hash(stored_hash, old_password):
            flash('Old password is incorrect.', 'danger')
            conn.close()
            return redirect(url_for('change_password'))
        
        # 5. UPDATED Hashing: Use generate_password_hash for the new password
        hashed_new_pwd = generate_password_hash(new_password)
        cursor.execute("UPDATE users1 SET password=? WHERE username=?", (hashed_new_pwd, username))
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
    init_db()  # Create database and table on first run
    # 6. Debug mode is OFF for deployment
    app.run(debug=False)
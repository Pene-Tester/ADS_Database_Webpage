from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key for production

# Database setup
def init_db():
    with sqlite3.connect("inventory.db") as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS items
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         item_name TEXT NOT NULL,
                         quantity INTEGER NOT NULL,
                         price REAL NOT NULL)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS users
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         username TEXT NOT NULL UNIQUE,
                         password TEXT NOT NULL,
                         role TEXT NOT NULL)''')
        # Add sample users if the table is empty
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            admin = ("admin", "adminpass", "admin")
            user = ("user", "userpass", "user")
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", admin)
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", user)
            conn.commit()

# Initialize database
init_db()

# Route to serve the login page or redirect to admin page if already logged in
@app.route("/")
def home():
    if 'username' in session and session['role'] == 'admin':
        return redirect(url_for('admin_dashboard'))
    return render_template("login.html")

# Route for login functionality
@app.route("/login", methods=["POST"])
def login():
    username = request.form['username']
    password = request.form['password']
    with sqlite3.connect("inventory.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()

    if user:
        session['username'] = user[1]  # Store username in session
        session['role'] = user[3]      # Store role in session
        if user[3] == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('user_dashboard'))
    else:
        flash('Invalid username or password')
        return redirect(url_for('home'))

# Route to serve the admin dashboard
@app.route("/admin_dashboard")
def admin_dashboard():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('home'))
    return render_template('admin.html', username=session['username'])

# Route to serve the user dashboard
@app.route("/user_dashboard")
def user_dashboard():
    if 'username' not in session or session['role'] != 'user':
        return redirect(url_for('home'))
    return render_template('user.html', username=session['username'])

# Route to serve the admin profile page
@app.route('/admin_profile')
def admin_profile():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('home'))

    with sqlite3.connect("inventory.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()

    return render_template('admin_profile.html', users=users, username=session['username'])

# Route to add a new user
@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('home'))

    if request.method == 'POST':
        # Handle form submission to add a new user
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        with sqlite3.connect("inventory.db") as conn:
            conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                         (username, password, 'user'))
        return redirect(url_for('admin_profile'))

    return render_template('add_user.html', username=session['username'])

# Route to delete a user
@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('home'))

    with sqlite3.connect("inventory.db") as conn:
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))

    return redirect(url_for('admin_profile'))

# API route to get all items
@app.route("/api/items", methods=["GET"])
def get_items():
    with sqlite3.connect("inventory.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM items")
        items = cursor.fetchall()
        return jsonify([{"id": i[0], "item_name": i[1], "quantity": i[2], "price": i[3]} for i in items])

# API route to add item
@app.route("/api/add_item", methods=["POST"])
def add_item():
    data = request.get_json()
    with sqlite3.connect("inventory.db") as conn:
        conn.execute("INSERT INTO items (item_name, quantity, price) VALUES (?, ?, ?)",
                     (data["item_name"], data["quantity"], data["price"]))
    return jsonify({"status": "Item added"}), 201

# API route to delete item
@app.route("/api/delete_item/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    with sqlite3.connect("inventory.db") as conn:
        conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
    return jsonify({"status": "Item deleted"}), 200

# Route to logout
@app.route("/logout")
def logout():
    session.clear()  # Clear all session data
    return redirect(url_for('home'))

# Prevent browser caching
@app.after_request
def after_request_func(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Expires'] = 0
    response.headers['Pragma'] = 'no-cache'
    return response

if __name__ == "__main__":
    app.run(debug=True)
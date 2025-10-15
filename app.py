from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from chatbot_model import get_response
import os

# --- INITIALIZATION ---

# 1. Flask App Setup
app = Flask(__name__)
# Use a secure, random secret key for session management
app.secret_key = os.urandom(24) 

# 2. Database Setup (using SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# 3. Bcrypt Initialization (for password hashing)
bcrypt = Bcrypt(app)

# --- DATABASE MODEL ---

class User(db.Model):
    """Represents a user in the database."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)

# Create the database tables if they don't exist
with app.app_context():
    db.create_all()

# --- AUTHENTICATION ROUTES ---

@app.route("/register", methods=["GET", "POST"])
def register():
    """Handles user registration."""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists. Please try another.", "error")
            return redirect(url_for("register"))
        
        # Hash the password before saving
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("login"))
        
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Handles user login."""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        
        # Check if user exists and password is correct
        if user and bcrypt.check_password_hash(user.password, password):
            # Store user info in the session
            session["user_id"] = user.id
            session["username"] = user.username
            session["language"] = 'en' # Default language on login
            flash("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password. Please try again.", "error")
            return redirect(url_for("login"))
            
    return render_template("admin_login.html")

@app.route("/logout")
def logout():
    """Logs the user out by clearing the session."""
    session.clear()
    flash("You have been successfully logged out.", "info")
    return redirect(url_for("login"))

# --- CORE APP ROUTES ---

@app.route("/")
def home():
    """Displays the main chatbot page if the user is logged in."""
    if "user_id" not in session:
        flash("Please log in to access the chatbot.", "info")
        return redirect(url_for("login"))
    
    # Get language from session, default to English
    language = session.get('language', 'en')
    
    return render_template("index.html", username=session.get("username"), language=language)

@app.route("/set_language", methods=["POST"])
def set_language():
    """API endpoint to change the user's language preference in the session."""
    lang = request.json.get("language")
    # Add all your supported languages to this list
    if lang in ['en', 'te', 'hi', 'ta', 'ml', 'kn']: 
        session['language'] = lang
        return jsonify({"status": "success", "language": lang})
    return jsonify({"status": "error", "message": "Invalid language"}), 400

@app.route("/get", methods=["POST"])
def chatbot_response():
    """API endpoint to get a response from the chatbot model."""
    if "user_id" not in session:
        return jsonify({"response": "Authentication error."}), 401

    user_message = request.json.get("message")
    if not user_message:
        return jsonify({"response": "No message received."}), 400

    # Get language from session to pass to the model
    lang = session.get('language', 'en')
    
    bot_reply = get_response(user_message, lang=lang)
    return jsonify({"response": bot_reply})

# --- RUN THE APP ---

if __name__ == "__main__":
    app.run(debug=True)

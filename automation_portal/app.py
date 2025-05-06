from flask import Flask, render_template, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key in production

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Pricing route
@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

# About route
@app.route('/about')
def about():
    return render_template('about.html')

# Login route
@app.route('/login')
def login():
    return render_template('login.html')

# Signup route
@app.route('/signup')
def signup():
    return render_template('signup.html')

# Dashboard route (requires user login in future)
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)

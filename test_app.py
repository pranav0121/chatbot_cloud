#!/usr/bin/env python3
"""
Minimal test Flask app to debug the blank page issue
"""
from flask import Flask, render_template

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test-secret-key'

@app.route('/')
def home():
    return "<h1>Test Flask App is Working!</h1>"

@app.route('/test-login')
def test_login():
    try:
        return render_template('login.html')
    except Exception as e:
        return f"Error rendering template: {str(e)}"

@app.route('/health')
def health():
    return "OK"

if __name__ == '__main__':
    print("Starting minimal test app...")
    app.run(debug=True, port=5002)

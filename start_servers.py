# app.py
import os
import sys
import threading
import time

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ============================================
# IMPORT BOTH DASHBOARDS
# ============================================

# Dashboard 1: Main Navigation (Port 8050)
from app_risk import app as app_risk

# Dashboard 2: Risk Calculator (Port 8051)
from prediction import app as prediction_app

# ============================================
# MULTI-APP DISPATCHER
# ============================================

# Create a Flask dispatcher that routes to both apps
from flask import Flask, request, redirect

# Get port from environment variable (Render sets this)
PORT = int(os.environ.get("PORT", 8050))

# Create a dispatcher app
app = Flask(__name__)

# Mount both Dash apps at different routes
# We'll use a simple dispatcher based on the path

@app.route('/')
def home():
    return redirect('/dashboard1')

@app.route('/dashboard1')
def dashboard1():
    # Serve app_risk
    return app_risk.server.full_dispatch_request()

@app.route('/dashboard2')
def dashboard2():
    # Serve prediction
    return prediction_app.server.full_dispatch_request()

# For Gunicorn
server = app

if __name__ == '__main__':
    # Run both servers in separate threads when running locally
    def run_app_risk():
        app_risk.run(host='0.0.0.0', port=8050, debug=False)
    
    def run_prediction():
        prediction_app.run(host='0.0.0.0', port=8051, debug=False)
    
    t1 = threading.Thread(target=run_app_risk)
    t2 = threading.Thread(target=run_prediction)
    t1.daemon = True
    t2.daemon = True
    t1.start()
    t2.start()
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[!] Shutting down...")

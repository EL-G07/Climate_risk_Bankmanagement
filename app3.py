# app.py
import os
import sys
import subprocess
import time
import threading

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ============================================
# IMPORT BOTH DASHBOARDS
# ============================================

# Import app_risk notebook as a module
import importlib.util


def load_notebook_as_module(notebook_path, module_name):
    """Load a Jupyter notebook as a Python module"""
    spec = importlib.util.spec_from_file_location(module_name, notebook_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Load both notebooks
try:
    # Try importing as regular Python modules first
    from app_risk import app as app_risk
except ImportError:
    # Fallback: load notebook directly
    app_risk_module = load_notebook_as_module('app_risk.ipynb', 'app_risk')
    app_risk = app_risk_module.app

try:
    from prediction import app as prediction_app
except ImportError:
    prediction_module = load_notebook_as_module('prediction.ipynb', 'prediction')
    prediction_app = prediction_module.app

# ============================================
# CREATE DISPATCHER APP
# ============================================

from flask import Flask, request, redirect

# Get port from environment (Render sets this)
PORT = int(os.environ.get("PORT", 8050))

# Create dispatcher app
app = Flask(__name__)


@app.route('/')
def home():
    return redirect('/dashboard1')


@app.route('/dashboard1')
def dashboard1():
    """Serve Main Dashboard (app_risk)"""
    # Mount the app at /dashboard1
    return app_risk.server.full_dispatch_request()


@app.route('/dashboard2')
def dashboard2():
    """Serve Risk Calculator (prediction)"""
    return prediction_app.server.full_dispatch_request()


# For Gunicorn
server = app

if __name__ == '__main__':
    # Run locally in development
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

    print("\n" + "=" * 60)
    print("  🌍 TANZANIA CLIMATE RISK DASHBOARD")
    print("=" * 60)
    print("  Main Dashboard:  http://127.0.0.1:8050")
    print("  Risk Calculator: http://127.0.0.1:8051")
    print("=" * 60 + "\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[!] Shutting down...")
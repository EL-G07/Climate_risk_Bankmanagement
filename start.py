# start.py
import os
import sys
import subprocess
import time
import threading


def run_notebook(notebook_path, port, name):
    """Execute a Jupyter notebook using IPython"""
    print(f"🚀 Starting {name} on port {port}...")

    # This command executes the notebook as a Python script
    cmd = [
        'ipython',
        '-c',
        f"exec(open('{notebook_path}').read())"
    ]

    # Start the process
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Check if it started
    time.sleep(5)
    if proc.poll() is None:
        print(f"✅ {name} is running on port {port}")
        return proc
    else:
        print(f"❌ {name} failed to start")
        return None


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("  🌍 TANZANIA CLIMATE RISK DASHBOARD")
    print("=" * 60)
    print("  Running from original .ipynb files (NO CONVERSION)")
    print("=" * 60 + "\n")

    # Start both notebooks
    processes = []

    # Notebook 1: app_risk.ipynb (Main Dashboard - Port 8050)
    proc1 = run_notebook('app_risk.ipynb', 8050, 'Main Dashboard')
    if proc1:
        processes.append(proc1)

    # Notebook 2: prediction.ipynb (Risk Calculator - Port 8051)
    proc2 = run_notebook('prediction.ipynb', 8051, 'Risk Calculator')
    if proc2:
        processes.append(proc2)

    print("\n" + "=" * 60)
    print("  ✅ DEPLOYMENT COMPLETE")
    print("=" * 60)
    print("  Main Dashboard:  http://0.0.0.0:8050")
    print("  Risk Calculator: http://0.0.0.0:8051")
    print("=" * 60)
    print("\n  Press Ctrl+C to stop all servers.\n")

    try:
        for proc in processes:
            proc.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        for proc in processes:
            proc.terminate()
            proc.wait()
        print("✅ Done.")
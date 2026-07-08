# start.py
import os
import sys
import subprocess
import time

print("\n" + "=" * 60)
print("  🌍 TANZANIA CLIMATE RISK DASHBOARD")
print("=" * 60)
print("  Running from original .ipynb files (NO CONVERSION)")
print("=" * 60 + "\n")


def run_notebook(notebook_path, port, name):
    print(f"🚀 Starting {name} on port {port}...")
    cmd = ['ipython', '-c', f"exec(open('{notebook_path}').read())"]
    proc = subprocess.Popen(cmd)
    time.sleep(5)
    if proc.poll() is None:
        print(f"✅ {name} is running on port {port}")
        return proc
    else:
        print(f"❌ {name} failed to start")
        return None


if __name__ == '__main__':
    processes = []
    proc1 = run_notebook('app_risk.ipynb', 8050, 'Main Dashboard')
    if proc1:
        processes.append(proc1)
    proc2 = run_notebook('prediction.ipynb', 8051, 'Risk Calculator')
    if proc2:
        processes.append(proc2)

    print("\n" + "=" * 60)
    print("  ✅ DEPLOYMENT COMPLETE")
    print("=" * 60)
    print("  Main Dashboard:  http://0.0.0.0:8050")
    print("  Risk Calculator: http://0.0.0.0:8051")
    print("=" * 60 + "\n")

    try:
        for proc in processes:
            proc.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        for proc in processes:
            proc.terminate()
            proc.wait()
        print("✅ Done.")
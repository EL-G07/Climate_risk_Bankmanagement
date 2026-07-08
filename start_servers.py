# start_servers.py
import subprocess
import time
import os
import sys
import signal
import webbrowser


def print_banner():
    """Print deployment banner"""
    print("\n" + "=" * 70)
    print("  🌍 TANZANIA CLIMATE RISK DASHBOARD")
    print("=" * 70)
    print("  📊 Deploying Dash Notebooks (No Conversion)")
    print("=" * 70 + "\n")


def check_notebooks(notebooks):
    """Check if all notebooks exist"""
    missing = []
    for notebook, _ in notebooks:
        if not os.path.exists(notebook):
            missing.append(notebook)

    if missing:
        print("❌ ERROR: Missing notebooks:")
        for nb in missing:
            print(f"   - {nb}")
        return False
    return True


def run_notebook(notebook, port):
    """
    Run a Jupyter notebook as a Dash server using IPython.
    The notebook executes and app.run() keeps it running.
    """
    print(f"  🚀 Starting: {notebook} (Port {port})")

    # Method: Use IPython to execute the notebook
    # This preserves all imports and runs the notebook exactly as-is
    cmd = [
        'ipython',
        '-c',
        f"""
import sys
sys.path.append('.')
exec(open('{notebook}').read())
"""
    ]

    # Start the process
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    return proc


def run_notebook_with_python(notebook, port):
    """
    Alternative: Use Python directly (no IPython needed)
    """
    print(f"  🚀 Starting: {notebook} (Port {port})")

    cmd = [
        'python',
        '-c',
        f"""
import sys
sys.path.append('.')
exec(open('{notebook}').read())
"""
    ]

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    return proc


def check_server(port, timeout=15):
    """
    Check if a server is running on the given port
    """
    import socket
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            if result == 0:
                return True
        except:
            pass
        time.sleep(1)

    return False


def stop_processes(processes):
    """Stop all running processes gracefully"""
    print("\n🛑 Shutting down servers...")

    for proc in processes:
        if proc.poll() is None:  # Still running
            proc.terminate()

    # Give them time to terminate
    time.sleep(2)

    # Force kill if still running
    for proc in processes:
        if proc.poll() is None:
            proc.kill()
            proc.wait()

    print("✅ All servers stopped.\n")


def open_browser():
    """Open browser to the dashboards"""
    time.sleep(3)
    webbrowser.open("http://127.0.0.1:8050")


if __name__ == "__main__":
    # ============================================================
    # CONFIGURATION: Edit these if your files are named differently
    # ============================================================
    notebooks = [
        ("app_risk.ipynb", 8050, "Main Dashboard"),
        ("prediction.ipynb", 8051, "Risk Calculator")
    ]
    # ============================================================

    print_banner()

    # Check files exist
    if not check_notebooks(notebooks):
        print("\n💡 Make sure all .ipynb files are in the current directory.")
        print("   Run this script from your project folder.\n")
        sys.exit(1)

    # Start each notebook
    print("📦 Starting servers...\n")
    processes = []

    for notebook, port, name in notebooks:
        # Use Python to execute (no IPython needed)
        proc = run_notebook_with_python(notebook, port)
        processes.append(proc)

        # Wait for server to start
        print(f"   ⏳ Waiting for {name} (Port {port})...")

        if check_server(port, timeout=15):
            print(f"   ✅ {name} is running on http://127.0.0.1:{port}")
        else:
            print(f"   ⚠️  {name} may not have started. Check logs.")

        print()

    # Open browser
    try:
        open_browser()
    except:
        pass

    # Print final status
    print("=" * 70)
    print("  ✅ DEPLOYMENT COMPLETE")
    print("=" * 70)
    print("  📍 Access your dashboards:")
    print()
    for _, port, name in notebooks:
        print(f"     • {name}: http://127.0.0.1:{port}")
    print()
    print("  🔗 The 'RISK CALC' button in Main Dashboard will")
    print("     automatically open the Risk Calculator in a new tab.")
    print("=" * 70)
    print("\n  Press Ctrl+C to stop all servers.\n")

    # Keep running
    try:
        while True:
            # Check if processes are still alive
            for proc in processes:
                if proc.poll() is not None:
                    # Process died
                    print(f"⚠️  A server stopped. Check logs.")
                    # Restart? For now, we'll just wait
            time.sleep(5)
    except KeyboardInterrupt:
        stop_processes(processes)
        sys.exit(0)
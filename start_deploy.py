# start_deploy.py
import os
import subprocess
import time
import sys


def run_notebook(notebook_path, port, name):
    """
    Executes a Jupyter notebook as a subprocess and keeps it running.
    """
    print(f"🚀 Starting {name} on port {port}...")

    # 1. Read the notebook and fix the 'null' error
    try:
        with open(notebook_path, 'r') as f:
            content = f.read()
        # Replace JavaScript 'null' with Python 'None'
        fixed_content = content.replace('null', 'None')
        print(f"   ✅ Fixed 'null' → 'None' in {notebook_path}")
    except FileNotFoundError:
        print(f"❌ Error: {notebook_path} not found.")
        return None

    # 2. Write the fixed content to a temporary Python file
    temp_file = notebook_path.replace('.ipynb', '_fixed.py')
    with open(temp_file, 'w') as f:
        f.write(fixed_content)

    # 3. Execute the fixed Python file with IPython
    #    Using IPython ensures that the environment is similar to Jupyter.
    cmd = [
        'ipython',
        '-c',
        f"exec(open('{temp_file}').read())"
    ]

    # 4. Start the subprocess and keep it alive
    proc = subprocess.Popen(cmd)

    # Give the server time to start
    time.sleep(8)

    # Check if the process is still running
    if proc.poll() is None:
        print(f"✅ {name} is running on port {port}")
        return proc
    else:
        print(f"❌ {name} failed to start. Check the logs above.")
        return None


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("  🌍 TANZANIA CLIMATE RISK DASHBOARD")
    print("=" * 60)
    print("  Deploying with automatic 'null' fix...")
    print("=" * 60 + "\n")

    processes = []

    # Start Main Dashboard
    proc1 = run_notebook('app_risk.ipynb', 8050, 'Main Dashboard')
    if proc1:
        processes.append(proc1)
    else:
        print("⚠️  Main Dashboard failed. Continuing with Risk Calculator...")

    # Start Risk Calculator
    proc2 = run_notebook('prediction.ipynb', 8051, 'Risk Calculator')
    if proc2:
        processes.append(proc2)
    else:
        print("⚠️  Risk Calculator failed.")

    if not processes:
        print("\n❌ No servers started. Deployment failed.")
        print("   Please check the error messages above.")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("  ✅ DEPLOYMENT SUCCESSFUL")
    print("=" * 60)
    print("  Main Dashboard:  http://0.0.0.0:8050")
    print("  Risk Calculator: http://0.0.0.0:8051")
    print("=" * 60 + "\n")
    print("  Press Ctrl+C to stop all servers.\n")

    try:
        # Keep the main script running
        for proc in processes:
            proc.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        for proc in processes:
            proc.terminate()
            proc.wait()
        print("✅ Done.")
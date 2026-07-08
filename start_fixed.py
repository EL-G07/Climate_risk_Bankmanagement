# start_deploy.py
import os
import subprocess
import time
import sys

def fix_notebook_and_run(notebook_path, port, name):
    """
    Reads a Jupyter notebook, replaces 'null' with 'None',
    writes it to a temporary file, and executes it.
    """
    print(f"🚀 Starting {name} on port {port}...")

    # 1. Read the notebook content
    try:
        with open(notebook_path, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ Error: {notebook_path} not found.")
        return None

    # 2. Replace 'null' with 'None'
    #    This is the core fix for the NameError.
    fixed_content = content.replace('null', 'None')

    # 3. Write the fixed content to a temporary Python file
    temp_file = notebook_path.replace('.ipynb', '_fixed.py')
    with open(temp_file, 'w') as f:
        f.write(fixed_content)

    # 4. Execute the fixed Python file
    #    We use 'python' directly instead of 'ipython' for reliability.
    cmd = ['python', temp_file]
    proc = subprocess.Popen(cmd)
    time.sleep(8)  # Give the server a moment to start

    if proc.poll() is None:
        print(f"✅ {name} is running on port {port}")
        return proc
    else:
        print(f"❌ {name} failed to start.")
        return None

if __name__ == '__main__':
    print("\n" + "="*60)
    print("  🌍 TANZANIA CLIMATE RISK DASHBOARD")
    print("="*60)
    print("  Deploying with automatic 'null' fix...")
    print("="*60 + "\n")

    processes = []
    proc1 = fix_notebook_and_run('app_risk.ipynb', 8050, 'Main Dashboard')
    if proc1:
        processes.append(proc1)

    proc2 = fix_notebook_and_run('prediction.ipynb', 8051, 'Risk Calculator')
    if proc2:
        processes.append(proc2)

    if not processes:
        print("\n❌ No servers started. Please check the logs for details.")
        sys.exit(1)

    print("\n" + "="*60)
    print("  ✅ DEPLOYMENT COMPLETE")
    print("="*60)
    print("  Main Dashboard:  http://0.0.0.0:8050")
    print("  Risk Calculator: http://0.0.0.0:8051")
    print("="*60 + "\n")
    print("  Press Ctrl+C to stop all servers.\n")

    try:
        for proc in processes:
            proc.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        for proc in processes:
            proc.terminate()
            proc.wait()
        print("✅ Done.")

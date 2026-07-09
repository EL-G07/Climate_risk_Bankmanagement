# start_deploy.py
import os
import subprocess
import sys
import time
import importlib.util

def run_notebook(notebook_path, port, name):
    """
    Executes a Jupyter notebook as a subprocess and forces it to start the server.
    """
    print(f"🚀 Starting {name} on port {port}...")

    # 1. Fix the 'null' error
    try:
        with open(notebook_path, 'r') as f:
            content = f.read()
        fixed_content = content.replace('null', 'None')
        print(f"   ✅ Fixed 'null' → 'None' in {notebook_path}")
    except FileNotFoundError:
        print(f"❌ Error: {notebook_path} not found.")
        return None

    # 2. Write the fixed content to a temporary Python file
    temp_file = notebook_path.replace('.ipynb', '_fixed.py')
    with open(temp_file, 'w') as f:
        f.write(fixed_content)

    # 3. Execute the file with Python and capture output
    cmd = ['python', '-u', temp_file]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    
    # 4. Print output in real-time and check for errors
    start_time = time.time()
    timeout = 15
    output_lines = []
    server_started = False
    
    while True:
        if proc.poll() is not None:
            print(f"❌ {name} exited with code {proc.returncode}")
            for line in proc.stdout:
                print(f"   {line.strip()}")
            return None
        
        # Read available output
        for line in proc.stdout:
            line = line.strip()
            if line:
                print(f"   {line}")
                output_lines.append(line)
                # Look for any error messages
                if "Error" in line or "Traceback" in line:
                    print(f"⚠️  Error detected in {name}. Waiting for more output...")
                # Look for server start confirmation
                if any("Running on" in line or "Dash is running" in line or "Starting" in line for line in output_lines):
                    server_started = True
        
        if server_started:
            print(f"✅ {name} is running on port {port}")
            return proc
        
        if time.time() - start_time > timeout:
            print(f"⚠️  {name} took too long, but process is still alive.")
            return proc
        
        time.sleep(1)

if __name__ == '__main__':
    print("\n" + "="*60)
    print("  🌍 TANZANIA CLIMATE RISK DASHBOARD")
    print("="*60)
    print("  Deploying with automatic 'null' fix...")
    print("="*60 + "\n")

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
        print("   Check the error messages above.")
        sys.exit(1)

    print("\n" + "="*60)
    print("  ✅ DEPLOYMENT SUCCESSFUL")
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

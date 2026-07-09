# start_wrapper.py
import os
import sys
import subprocess
import time


def run_notebook_safe(notebook_path, port, name):
    """Run a notebook with a wrapper that ensures app is defined"""
    print(f"🚀 Starting {name} on port {port}...")

    # Create a wrapper script that imports the notebook and runs app
    wrapper_code = f'''
import sys
sys.path.append('.')
import importlib.util

# Load the notebook as a module
spec = importlib.util.spec_from_file_location("notebook", "{notebook_path}")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# Try to get the app object
app = getattr(module, 'app', None)
if app is None:
    print("Error: 'app' not found in notebook")
    sys.exit(1)

# Start the server
app.run(host='0.0.0.0', port={port}, debug=False, use_reloader=False)
'''

    # Write the wrapper
    wrapper_file = f"wrapper_{name.replace(' ', '_')}.py"
    with open(wrapper_file, 'w') as f:
        f.write(wrapper_code)

    # Run the wrapper
    cmd = ['python', '-u', wrapper_file]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    # Monitor output
    start_time = time.time()
    timeout = 15
    server_started = False

    while True:
        if proc.poll() is not None:
            print(f"❌ {name} exited with code {proc.returncode}")
            for line in proc.stdout:
                print(f"   {line.strip()}")
            return None

        for line in proc.stdout:
            line = line.strip()
            if line:
                print(f"   {line}")
                if "Running on" in line or "Dash is running" in line:
                    server_started = True

        if server_started:
            print(f"✅ {name} is running on port {port}")
            return proc

        if time.time() - start_time > timeout:
            print(f"⚠️  {name} took too long, but process is still alive.")
            return proc

        time.sleep(1)


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("  🌍 TANZANIA CLIMATE RISK DASHBOARD")
    print("=" * 60)
    print("  Deploying with wrapper script...")
    print("=" * 60 + "\n")

    processes = []

    proc1 = run_notebook_safe('app_risk.ipynb', 8050, 'Main Dashboard')
    if proc1:
        processes.append(proc1)

    proc2 = run_notebook_safe('prediction.ipynb', 8051, 'Risk Calculator')
    if proc2:
        processes.append(proc2)

    if not processes:
        print("\n❌ No servers started. Deployment failed.")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("  ✅ DEPLOYMENT SUCCESSFUL")
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
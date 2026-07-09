# start_deploy.py
import os
import sys
import subprocess
import time
import importlib.util

def run_notebook(notebook_path, port, name):
    """
    Executes a Jupyter notebook as a module and starts the server.
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

    # 3. Create a runner script that imports the module and starts the app
    runner_code = f'''
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the fixed notebook as a module
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("notebook_module", "{temp_file}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Try to get the app object from multiple places
    app = None
    
    # Check if 'app' is in the module
    if hasattr(module, 'app'):
        app = module.app
    else:
        # Try to find any Dash app in the module
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if hasattr(attr, '__class__') and 'Dash' in str(attr.__class__):
                app = attr
                print(f"   Found Dash app as: {{attr_name}}")
                break
    
    # If app is still None, try to find it in the module's globals
    if app is None:
        # Look for a Dash app in the module's global variables
        for key, value in module.__dict__.items():
            if hasattr(value, '__class__') and 'Dash' in str(value.__class__):
                app = value
                print(f"   Found Dash app as global: {{key}}")
                break
    
    if app is None:
        print("Error: 'app' not found in notebook")
        print("   Available attributes:", [attr for attr in dir(module) if not attr.startswith('_')])
        sys.exit(1)
    
    # Start the server
    print(f"Starting server on port {port}...")
    app.run(host='0.0.0.0', port={port}, debug=False, use_reloader=False)
    
except Exception as e:
    print(f"Error: {{e}}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
'''
    
    # Write the runner
    runner_file = f"runner_{name.replace(' ', '_')}.py"
    with open(runner_file, 'w') as f:
        f.write(runner_code)
    
    # 4. Execute the runner with Python
    cmd = ['python', '-u', runner_file]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    
    # 5. Print output in real-time
    start_time = time.time()
    timeout = 15
    server_started = False
    
    while True:
        if proc.poll() is not None:
            print(f"❌ {name} exited with code {proc.returncode}")
            for line in proc.stdout:
                if line.strip():
                    print(f"   {line.strip()}")
            return None
        
        for line in proc.stdout:
            line = line.strip()
            if line:
                print(f"   {line}")
                if "Running on" in line or "Starting server" in line:
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
    print("  Deploying with importlib wrapper...")
    print("="*60 + "\n")

    processes = []
    
    proc1 = run_notebook('app_risk.ipynb', 8050, 'Main Dashboard')
    if proc1:
        processes.append(proc1)
    else:
        print("⚠️  Main Dashboard failed. Continuing with Risk Calculator...")

    proc2 = run_notebook('prediction.ipynb', 8051, 'Risk Calculator')
    if proc2:
        processes.append(proc2)
    else:
        print("⚠️  Risk Calculator failed.")

    if not processes:
        print("\n❌ No servers started. Deployment failed.")
        sys.exit(1)

    print("\n" + "="*60)
    print("  ✅ DEPLOYMENT SUCCESSFUL")
    print("="*60)
    print("  Main Dashboard:  http://0.0.0.0:8050")
    print("  Risk Calculator: http://0.0.0.0:8051")
    print("="*60 + "\n")

    try:
        for proc in processes:
            proc.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        for proc in processes:
            proc.terminate()
            proc.wait()
        print("✅ Done.")

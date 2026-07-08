# start_fixed.py - FIXED version (replaces null → None)
import os
import sys# start_fixed.py - Improved version
import os
import sys
import subprocess
import time
import traceback

print("\n" + "="*60)
print("  🌍 TANZANIA CLIMATE RISK DASHBOARD")
print("="*60)
print("  Running with improved error handling")
print("="*60 + "\n")

def run_notebook_safe(notebook_path, port, name):
    """Execute a notebook with better error handling"""
    print(f"🚀 Starting {name} on port {port}...")
    
    try:
        # Use Python directly instead of IPython
        cmd = [
            'python', '-c',
            f"""
import sys
sys.path.append('.')
try:
    exec(open('{notebook_path}').read())
except Exception as e:
    print(f"Error in {name}: {{e}}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
"""
        ]
        
        proc = subprocess.Popen(cmd)
        time.sleep(8)
        
        if proc.poll() is None:
            print(f"✅ {name} is running on port {port}")
            return proc
        else:
            print(f"❌ {name} failed to start")
            return None
            
    except Exception as e:
        print(f"❌ Error starting {name}: {e}")
        return None

if __name__ == '__main__':
    processes = []
    
    # Try each notebook
    proc1 = run_notebook_safe('app_risk.ipynb', 8050, 'Main Dashboard')
    if proc1:
        processes.append(proc1)
    
    proc2 = run_notebook_safe('prediction.ipynb', 8051, 'Risk Calculator')
    if proc2:
        processes.append(proc2)
    
    if not processes:
        print("\n❌ No servers started. Please check your notebooks.")
        print("   Try running the app.py test first.")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("  ✅ DEPLOYMENT COMPLETE")
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
import subprocess
import time

print("\n" + "=" * 60)
print("  🌍 TANZANIA CLIMATE RISK DASHBOARD")
print("=" * 60)
print("  Running with null → None fix")
print("=" * 60 + "\n")


def fix_notebook(notebook_path):
    """Read notebook and replace 'null' with 'None'"""
    with open(notebook_path, 'r') as f:
        content = f.read()

    # Replace JavaScript null with Python None
    content = content.replace('null', 'None')

    # Write to a temporary file
    temp_path = notebook_path.replace('.ipynb', '_fixed.ipynb')
    with open(temp_path, 'w') as f:
        f.write(content)

    print(f"   ✅ Fixed {notebook_path} (null → None)")
    return temp_path


def run_notebook(notebook_path, port, name):
    print(f"🚀 Starting {name} on port {port}...")

    # Fix the notebook
    fixed_path = fix_notebook(notebook_path)

    # Execute the fixed notebook
    cmd = ['ipython', '-c', f"exec(open('{fixed_path}').read())"]
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

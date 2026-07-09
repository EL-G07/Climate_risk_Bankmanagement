"""
run_app.py

Deployment launcher. Does NOT modify app_risk.ipynb or prediction.ipynb.

What it does, every time the container starts:
  1. Uses `jupyter nbconvert --to script` to produce throwaway .py copies of
     app_risk.ipynb and prediction.ipynb in a scratch directory. This is a
     read-only conversion - your original .ipynb files on disk are untouched.
  2. Runs each generated script as its own subprocess on a fixed internal
     port (8050 for the main dashboard, 8051 for the risk calculator).
     The risk calculator subprocess gets DASH_ROUTES_PATHNAME_PREFIX and
     DASH_REQUESTS_PATHNAME_PREFIX set to "/risk-calc/" - Dash reads these
     env vars automatically, so its pages/assets/callbacks all live under
     /risk-calc/ without touching a single line of prediction.ipynb.
  3. Starts proxy_server.py bound to Render's $PORT, which forwards
     /risk-calc/* to the port-8051 process and everything else to the
     port-8050 process. Render (and most single-port PaaS hosts) only
     exposes one port per web service, so this proxy is what makes both
     pages reachable from one public URL.

IMPORTANT - two lines in your notebooks still need to change for the
in-app navigation buttons to work for real visitors (see chat message):
  - app_risk.ipynb:   RISK_CALC_URL = "http://127.0.0.1:8051"
  - prediction.ipynb: href="http://127.0.0.1:8050" (Back to Home button)
These are literal browser-side links, so no server-side proxy or env var
can rewrite them - only editing that string will fix the click-through.
"""
import os
import subprocess
import sys
import time
import urllib.request
import urllib.error

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRATCH_DIR = "/tmp/_generated"
os.makedirs(SCRATCH_DIR, exist_ok=True)

DASHBOARD_PORT = "8050"
RISK_CALC_PORT = "8051"


def convert_notebook(notebook_name):
    """Read-only conversion: notebook.ipynb -> scratch/notebook.py. Source file untouched."""
    out_path = os.path.join(SCRATCH_DIR, notebook_name.replace(".ipynb", ""))
    subprocess.run(
        [
            sys.executable, "-m", "jupyter", "nbconvert",
            "--to", "script",
            os.path.join(BASE_DIR, notebook_name),
            "--output", out_path,
        ],
        check=True,
        cwd=BASE_DIR,
    )
    return out_path + ".py"


def wait_for(port, path="/", timeout=20):
    start = time.time()
    while time.time() - start < timeout:
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=2)
            return True
        except urllib.error.HTTPError:
            # Any HTTP response (even a 404) means the server is up and listening.
            return True
        except Exception:
            time.sleep(1)
    return False


def main():
    dashboard_script = convert_notebook("app_risk.ipynb")
    risk_calc_script = convert_notebook("prediction.ipynb")

    dashboard_env = os.environ.copy()
    dashboard_env["PORT"] = DASHBOARD_PORT
    dashboard_env.pop("DASH_ROUTES_PATHNAME_PREFIX", None)
    dashboard_env.pop("DASH_REQUESTS_PATHNAME_PREFIX", None)

    risk_calc_env = os.environ.copy()
    risk_calc_env["PORT"] = RISK_CALC_PORT
    risk_calc_env["DASH_ROUTES_PATHNAME_PREFIX"] = "/risk-calc/"
    risk_calc_env["DASH_REQUESTS_PATHNAME_PREFIX"] = "/risk-calc/"

    print("Starting Main Dashboard (app_risk.ipynb) on internal port", DASHBOARD_PORT, flush=True)
    dashboard_proc = subprocess.Popen(
        [sys.executable, dashboard_script], cwd=BASE_DIR, env=dashboard_env
    )

    print("Starting Risk Calculator (prediction.ipynb) on internal port", RISK_CALC_PORT, flush=True)
    risk_calc_proc = subprocess.Popen(
        [sys.executable, risk_calc_script], cwd=BASE_DIR, env=risk_calc_env
    )

    if not wait_for(DASHBOARD_PORT, "/"):
        print("ERROR: Main Dashboard did not start in time.", flush=True)
    if not wait_for(RISK_CALC_PORT, "/risk-calc/"):
        print("ERROR: Risk Calculator did not start in time.", flush=True)

    print("Starting reverse proxy on", os.environ.get("PORT", "8080"), flush=True)
    proxy_env = os.environ.copy()
    proxy_proc = subprocess.Popen(
        [sys.executable, os.path.join(BASE_DIR, "proxy_server.py")], cwd=BASE_DIR, env=proxy_env
    )

    # The proxy is the only process Render actually depends on to keep the
    # container "up". If one of the two notebook apps crashes (e.g. a bug in
    # that notebook), we don't want to take down the other one too - keep
    # whichever pages still work reachable, and just log the failure loudly.
    labels = {dashboard_proc.pid: "Main Dashboard (app_risk.ipynb)",
              risk_calc_proc.pid: "Risk Calculator (prediction.ipynb)"}
    reported = set()
    try:
        while True:
            if proxy_proc.poll() is not None:
                print("Reverse proxy exited unexpectedly. Shutting down.", flush=True)
                for p in (dashboard_proc, risk_calc_proc):
                    if p.poll() is None:
                        p.terminate()
                sys.exit(proxy_proc.returncode or 1)

            for p in (dashboard_proc, risk_calc_proc):
                if p.poll() is not None and p.pid not in reported:
                    reported.add(p.pid)
                    print(
                        f"WARNING: {labels.get(p.pid, p.pid)} exited with code {p.returncode}. "
                        "Its page will show a connection error until this is fixed and the "
                        "service is redeployed. Other pages keep running.",
                        flush=True,
                    )
            time.sleep(2)
    except KeyboardInterrupt:
        for p in (dashboard_proc, risk_calc_proc, proxy_proc):
            if p.poll() is None:
                p.terminate()


if __name__ == "__main__":
    main()

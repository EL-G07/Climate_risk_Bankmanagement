"""
_run_notebook_script.py

Installs notebook_import_shim.py (a modern replacement for the broken
import_ipynb package - see that file for why) and then runs the given
nbconvert-generated script exactly as if it had been executed directly
(__name__ == '__main__', so its own `if __name__ == '__main__': app.run(...)`
guard fires normally).

Usage: python _run_notebook_script.py /path/to/generated_script.py
"""
import sys

import notebook_import_shim  # noqa: F401  (import installs the shim)

if __name__ == "__main__":
    script_path = sys.argv[1]
    with open(script_path, "r", encoding="utf-8") as f:
        source = f.read()
    code = compile(source, script_path, "exec")
    exec(code, {"__name__": "__main__", "__file__": script_path})

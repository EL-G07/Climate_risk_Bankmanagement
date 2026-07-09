"""
notebook_import_shim.py

Why this exists: prediction.ipynb and Financial_risk_tool.ipynb both do
`import import_ipynb` so they can `import` a sibling notebook (e.g.
`import Financial_risk_tool as fr`). That package hasn't been updated since
~2018 and only implements the old find_module()/load_module() import
protocol. Python 3.12+ (and 3.13, which Render's base image uses) dropped
support for that legacy protocol entirely - import_ipynb's finder sits in
sys.meta_path but is simply never called, so the import silently fails with
ModuleNotFoundError no matter what PYTHONPATH or cwd is set to.

This module is a drop-in, modern (PEP 451: find_spec/exec_module) equivalent
with the same behavior: `import Some_Notebook` looks for `Some_Notebook.ipynb`
(also trying underscores-as-spaces) on sys.path or the current directory, and
executes its code cells to build the module - same as import_ipynb did.

None of the .ipynb files need to change. They can keep their existing
`import import_ipynb` line (harmless - it just registers the old, unused
finder alongside this one); this shim is installed by run_app.py before the
generated scripts run.
"""
import importlib.abc
import importlib.util
import os
import sys

import nbformat


def _find_notebook_path(name, search_dirs):
    for d in search_dirs:
        if not d:
            d = os.getcwd()
        for candidate in (name, name.replace("_", " ")):
            path = os.path.join(d, candidate + ".ipynb")
            if os.path.isfile(path):
                return path
    return None


class NotebookLoader(importlib.abc.Loader):
    def __init__(self, path):
        self.path = path

    def create_module(self, spec):
        return None  # default module creation is fine

    def exec_module(self, module):
        nb = nbformat.read(self.path, as_version=4)
        module.__file__ = self.path
        for cell in nb.cells:
            if cell.cell_type == "code":
                code = compile(cell.source, self.path, "exec")
                exec(code, module.__dict__)


class NotebookFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        if "." in fullname:
            return None  # only handle simple top-level notebook imports
        search_dirs = list(path) if path else (sys.path + [os.getcwd()])
        nb_path = _find_notebook_path(fullname, search_dirs)
        if nb_path is None:
            return None
        return importlib.util.spec_from_loader(fullname, NotebookLoader(nb_path))


def install():
    if not any(isinstance(f, NotebookFinder) for f in sys.meta_path):
        sys.meta_path.append(NotebookFinder())


install()

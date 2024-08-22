import sys
from cx_Freeze import setup, Executable

target_script = "Master.py"

build_exe_options = {
    "packages": ["tkinter", "pandas", "json"],
    "excludes": [],
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

executables = [Executable(target_script, base=base)]

setup(
    name="Arena APP",
    version="1.0",
    description="Arena APP",
    options={"build_exe": build_exe_options},
    executables=executables,
)

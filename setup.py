import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "packages": ["os", "PyQt6", "sqlite3", "pandas", "openpyxl"],
    "excludes": ["tkinter"],
    "include_files": []
}

# GUI applications require a different base on Windows (the default is for a console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="AgroFarm Manager",
    version="1.0",
    description="Система обліку та планування вирощування культур",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base, 
                           target_name="AgroFarmManager.exe",
                           icon="icon.ico")]
)
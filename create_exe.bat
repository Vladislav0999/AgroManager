@echo off
echo ========================================
echo Створення EXE файлу AgroFarm Manager
echo ========================================
echo.

REM 1. Очищення старих файлів
echo [1/4] Очищення старих файлів...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "AgroFarmManager.spec" del AgroFarmManager.spec
echo ✓ Готово!

REM 2. Перевірка встановлення PyInstaller
echo [2/4] Перевірка PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo ! PyInstaller не встановлено, встановлюю...
    pip install pyinstaller
) else (
    echo ✓ PyInstaller вже встановлений
)

REM 3. Створення EXE
echo [3/4] Створення EXE файлу...
pyinstaller --onefile --windowed --name AgroFarmManager main.py

REM 4. Копіювання до папки release
echo [4/4] Копіювання файлів...
if not exist "release" mkdir release
copy dist\AgroFarmManager.exe release\ 2>nul
copy agrofarm.db release\ 2>nul

echo.
echo ========================================
echo ✅ ГОТОВО!
echo ========================================
echo.
echo 📁 EXE файл: release\AgroFarmManager.exe
echo 📁 База даних: release\agrofarm.db
echo.
echo Запустіть EXE файл з папки release!
echo.
pause
@echo off
cd /d "%~dp0"
python -m PyInstaller --noconfirm --clean ^
  --windowed ^
  --onefile ^
  --name HarbourMaster ^
  --icon "assets\hm_icon_v3.ico" ^
  --collect-all customtkinter ^
  --add-data "assets\hm_icon_v3.ico;assets" ^
  --add-data "assets\hm_icon_v3.png;assets" ^
  --add-data "assets\hm_logo.gif;assets" ^
  --add-data "assets\discord.png;assets" ^
  --add-data "assets\anim;assets/anim" ^
  --add-data "assets\games;assets/games" ^
  --distpath "dist" ^
  --workpath "build" ^
  main.py
if errorlevel 1 (
  echo Build failed.
  pause
  exit /b 1
)

echo.
echo Copying EXE to project root...
copy /Y "dist\HarbourMaster.exe" "%~dp0HarbourMaster.exe"
copy /Y "dist\HarbourMaster.exe" "%USERPROFILE%\Desktop\HarbourMaster.exe"
copy /Y "assets\hm_icon_v3.ico" "%USERPROFILE%\Desktop\HarbourMaster.ico"

echo.
echo Built:
echo   %~dp0HarbourMaster.exe
echo   dist\HarbourMaster.exe
echo   Desktop\HarbourMaster.exe
echo.
echo Zip HarbourMaster.exe (+ README) as HMLauncher.zip to share with users.
pause

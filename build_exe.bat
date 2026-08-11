@echo off
cd /d "%~dp0"
python -m PyInstaller --noconfirm --clean ^
  --windowed ^
  --onefile ^
  --name ShipYard ^
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
copy /Y "dist\ShipYard.exe" "%~dp0ShipYard.exe"
copy /Y "dist\ShipYard.exe" "%USERPROFILE%\Desktop\ShipYard.exe"
copy /Y "assets\hm_icon_v3.ico" "%USERPROFILE%\Desktop\ShipYard.ico"

echo.
echo Built:
echo   %~dp0ShipYard.exe
echo   dist\ShipYard.exe
echo   Desktop\ShipYard.exe
echo.
echo Zip ShipYard.exe (+ README) as ShipYard-vX.Y.Z.zip to share with users.
pause

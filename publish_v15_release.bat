@echo off
cd /d "%~dp0"
echo.
echo === HarbourMaster v1.5.0 release helper ===
echo Commit and push source from Command Prompt first, then run this.
echo.

gh auth status >nul 2>&1
if errorlevel 1 (
  echo Run: gh auth login
  pause
  exit /b 1
)

if not exist "dist\HMLauncher-v1.5.0.zip" (
  echo Missing dist\HMLauncher-v1.5.0.zip
  echo Run build_exe.bat, then recreate the zip.
  pause
  exit /b 1
)

gh release create v1.5.0 "dist\HMLauncher-v1.5.0.zip" ^
  --repo RaccoonCloud/HM-Launcher ^
  --title "HarbourMaster v1.5.0" ^
  --notes-file "RELEASE_NOTES_v1.5.0.md"

if errorlevel 1 (
  echo Release failed.
  pause
  exit /b 1
)

echo.
echo https://github.com/RaccoonCloud/HM-Launcher/releases/tag/v1.5.0
pause

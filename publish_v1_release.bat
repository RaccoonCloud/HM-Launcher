@echo off
cd /d "%~dp0"
echo.
echo === HarbourMaster v1.0.0 release helper ===
echo Run this in Command Prompt AFTER you have committed and pushed source.
echo.

gh auth status >nul 2>&1
if errorlevel 1 (
  echo You need to log in to GitHub CLI once:
  echo   gh auth login
  echo Choose GitHub.com, HTTPS, and log in with browser.
  pause
  exit /b 1
)

if not exist "dist\HMLauncher-v1.0.0.zip" (
  echo Missing dist\HMLauncher-v1.0.0.zip - run build_exe.bat first, then rebuild the zip.
  pause
  exit /b 1
)

gh release create v1.0.0 "dist\HMLauncher-v1.0.0.zip" ^
  --repo RaccoonCloud/HM-Launcher ^
  --title "HarbourMaster v1.0.0" ^
  --notes-file "RELEASE_NOTES_v1.0.0.md"

if errorlevel 1 (
  echo Release failed. If v1.0.0 already exists, delete it on GitHub or use a new tag.
  pause
  exit /b 1
)

echo.
echo Release published:
echo https://github.com/RaccoonCloud/HM-Launcher/releases/tag/v1.0.0
pause

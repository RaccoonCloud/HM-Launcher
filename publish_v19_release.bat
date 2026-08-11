@echo off
cd /d "%~dp0"
echo === ShipYard v1.9.0 release helper ===
echo.
echo This only creates the GitHub release. Commit/push from CMD yourself first.
echo.

where gh >nul 2>&1
if errorlevel 1 (
  echo GitHub CLI (gh) not found. Install it, then run: gh auth login
  pause
  exit /b 1
)

if not exist "dist\ShipYard-v1.9.0.zip" (
  echo Missing dist\ShipYard-v1.9.0.zip - run build_exe.bat, then zip ShipYard.exe + README.
  pause
  exit /b 1
)

gh release create v1.9.0 "dist\ShipYard-v1.9.0.zip" ^
  --repo RaccoonCloud/ShipYard ^
  --title "ShipYard v1.9.0" ^
  --notes-file "RELEASE_NOTES_v1.9.0.md"

if errorlevel 1 (
  echo Release create failed.
  pause
  exit /b 1
)

echo.
echo Done. Release: https://github.com/RaccoonCloud/ShipYard/releases/tag/v1.9.0
pause

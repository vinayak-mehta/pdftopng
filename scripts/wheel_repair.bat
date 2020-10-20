@echo off

set WHEEL=%1
set DEST_DIR=%2

pip install pefile machomachomangler
python scripts/wheel_repair.py %WHEEL% -d %VCPKG_INSTALLATION_ROOT%\installed\x64-windows\bin -w %DEST_DIR%

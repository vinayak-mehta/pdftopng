@echo off

vcpkg install freetype:x86-windows fontconfig:x86-windows libpng:x86-windows libjpeg-turbo:x86-windows
Rem set PATH=%PATH%;.\vcpkg\installed\x86-windows\bin

cd lib\poppler
mkdir build_x86 && cd build_x86
cmake -A Win32 -DCMAKE_TOOLCHAIN_FILE=%VCPKG_INSTALLATION_ROOT%/scripts/buildsystems/vcpkg.cmake -DENABLE_QT5=OFF -DENABLE_LIBOPENJPEG=none -DENABLE_CPP=OFF ..
cmake --build . --config Release --target poppler
cd ..\..\..

@echo off

vcpkg install freetype:x86-windows fontconfig:x86-windows libpng:x86-windows libjpeg-turbo:x86-windows
Rem set PATH=%PATH%;.\vcpkg\installed\x86-windows\bin

cd lib\poppler

mkdir build_win_x86
cd build_win_x86

Rem https://cmake.org/cmake/help/latest/generator/Visual%20Studio%2016%202019.html#platform-selection
cmake -A Win32 -DCMAKE_TOOLCHAIN_FILE=%VCPKG_INSTALLATION_ROOT%/scripts/buildsystems/vcpkg.cmake -DENABLE_QT5=OFF -DENABLE_LIBOPENJPEG=none -DENABLE_CPP=OFF -DENABLE_BOOST=OFF ..
cmake --build . --config Release --target poppler

cd ..\..\..

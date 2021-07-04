@echo off

vcpkg install freetype:x64-windows fontconfig:x64-windows libpng:x64-windows libjpeg-turbo:x64-windows
Rem set PATH=%PATH%;.\vcpkg\installed\x64-windows\bin

cd lib\poppler

mkdir build_win_x64
cd build_win_x64

Rem https://cmake.org/cmake/help/latest/generator/Visual%20Studio%2016%202019.html#platform-selection
cmake -A x64 -DCMAKE_TOOLCHAIN_FILE=%VCPKG_INSTALLATION_ROOT%\scripts\buildsystems\vcpkg.cmake -DENABLE_QT5=OFF -DENABLE_LIBOPENJPEG=none -DENABLE_CPP=OFF -DENABLE_BOOST=OFF ..
cmake --build . --config Release --target poppler

cd ..\..\..

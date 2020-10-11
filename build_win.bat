@echo off

Rem Install vcpkg

vcpkg.exe install freetype:x64-windows fontconfig:x64-windows libpng:x64-windows libjpeg-turbo:x64-windows
set PATH=%PATH%;C:\dev\vcpkg\installed\x64-windows\bin

cd lib\poppler
mkdir build && cd build
cmake -DCMAKE_TOOLCHAIN_FILE=C:/dev/vcpkg/scripts/buildsystems/vcpkg.cmake -D ENABLE_QT5=OFF -D ENABLE_LIBOPENJPEG=none -D ENABLE_CPP=OFF ..
cmake --build . --config Release --target poppler

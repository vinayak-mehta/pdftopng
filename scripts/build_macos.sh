#!/bin/bash

brew install pkg-config freetype fontconfig libpng jpeg

cd lib/poppler
mkdir build
cd build
cmake -D CMAKE_FIND_FRAMEWORK=LAST -D ENABLE_QT5=OFF -D ENABLE_LIBOPENJPEG=none -D ENABLE_CPP=OFF -D ENABLE_BOOST=OFF ..
make poppler

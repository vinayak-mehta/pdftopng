#!/bin/bash

brew install freetype fontconfig libpng jpeg

cd lib/poppler
mkdir build && cd build
cmake -D ENABLE_QT5=OFF -D ENABLE_LIBOPENJPEG=none -D ENABLE_CPP=OFF ..
make poppler

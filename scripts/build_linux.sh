#!/bin/bash

yum install -y cmake3 freetype-devel fontconfig-devel libpng-devel libjpeg-devel

cd lib/poppler
mkdir build && cd build
cmake3 -D ENABLE_QT5=OFF -D ENABLE_LIBOPENJPEG=none -D ENABLE_CPP=OFF ..
make poppler

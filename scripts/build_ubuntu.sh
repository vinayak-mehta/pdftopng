#!/bin/bash

apt install cmake libfreetype-dev libfontconfig-dev libpng-dev libjpeg-dev

cd lib/poppler
mkdir build && cd build
cmake -D ENABLE_QT5=OFF -D ENABLE_LIBOPENJPEG=none -D ENABLE_CPP=OFF -D ENABLE_BOOST=OFF ..
make poppler

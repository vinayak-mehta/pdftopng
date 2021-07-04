#!/bin/bash

yum install -y wget freetype-devel fontconfig-devel libpng-devel libjpeg-devel

wget https://cmake.org/files/v3.10/cmake-3.10.2.tar.gz
tar zxvf cmake-3.10.2.tar.gz
current_directory=$(pwd)

cd lib/poppler
mkdir build && cd build
$(current_directory)/cmake-3.10.2-Linux-x86_64/bin/cmake -D ENABLE_QT5=OFF -D ENABLE_LIBOPENJPEG=none -D ENABLE_CPP=OFF -D ENABLE_BOOST=OFF ..
make poppler

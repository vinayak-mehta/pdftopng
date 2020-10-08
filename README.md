# poppler-utils

Precompiled command-line utilities (based on Poppler) for manipulating PDF files and converting them to other formats.

## Build

You'll need `g++`, `cmake`, and `pybind11` to build everything.

- First, we need to build `poppler`.

```
$ cd poppler
$ mkdir build && cd build
& cmake ..
& make poppler
```

- Then we need to build the `pdftopng` shared library:

```
$ g++ -Ipoppler -Ipoppler/fofi -Ipoppler/goo -Ipoppler/poppler -Ipoppler/build -Ipoppler/build/poppler -Ipoppler/utils -Ipoppler/build/utils -I/usr/include/python3.8 -I/home/vinayak/.virtualenvs/poppler-dev/lib/python3.8/site-packages/pybind11/include -O3 -Wall -Wl,-rpath,poppler/build: -shared -std=c++14 -fPIC -o pdftopng.cpython-38-x86_64-linux-gnu.so poppler_utils/pdftopng.cc -Lpoppler/build poppler/build/libpoppler.so
$ ls
pdftopng.cpython-38-x86_64-linux-gnu.so
```

## Usage

```
>>> import pdftopng
>>> pdftopng.convert(pdf_path="foo.pdf", png_path="foo")
>>>
```

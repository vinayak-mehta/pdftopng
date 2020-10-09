# poppler-utils

Precompiled command-line utilities (based on Poppler) for manipulating PDF files and converting them to other formats.

## Build

We need `g++`, `cmake`, and `pybind11` to build everything.

- First, we need to build `poppler`.

```
$ cd poppler
$ mkdir build && cd build
& cmake ..
& make poppler
```

- Then we can install `poppler-utils` using `pip`:

```
$ pip install .
```

`-Wl,-rpath,poppler/build:`

## Usage

```
>>> import pdftopng
>>> pdftopng.convert(pdf_path="foo.pdf", png_path="foo")
>>>
```

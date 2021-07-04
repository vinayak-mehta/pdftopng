//========================================================================
//
// pdftopng.cpp
//
// Copyright 2003 Glyph & Cog, LLC
//
//========================================================================

//========================================================================
//
// Modified under the Poppler project - http://poppler.freedesktop.org
//
// All changes made under the Poppler project to this file are licensed
// under GPL version 2 or later
//
// Copyright (C) 2007 Ilmari Heikkinen <ilmari.heikkinen@gmail.com>
// Copyright (C) 2008 Richard Airlie <richard.airlie@maglabs.net>
// Copyright (C) 2009 Michael K. Johnson <a1237@danlj.org>
// Copyright (C) 2009 Shen Liang <shenzhuxi@gmail.com>
// Copyright (C) 2009 Stefan Thomas <thomas@eload24.com>
// Copyright (C) 2009-2011, 2015, 2018-2021 Albert Astals Cid <aacid@kde.org>
// Copyright (C) 2010, 2012, 2017 Adrian Johnson <ajohnson@redneon.com>
// Copyright (C) 2010 Hib Eris <hib@hiberis.nl>
// Copyright (C) 2010 Jonathan Liu <net147@gmail.com>
// Copyright (C) 2010 William Bader <williambader@hotmail.com>
// Copyright (C) 2011-2013 Thomas Freitag <Thomas.Freitag@alfa.de>
// Copyright (C) 2013, 2015, 2018 Adam Reichold <adamreichold@myopera.com>
// Copyright (C) 2013 Suzuki Toshiya <mpsuzuki@hiroshima-u.ac.jp>
// Copyright (C) 2015 William Bader <williambader@hotmail.com>
// Copyright (C) 2018 Martin Packman <gzlist@googlemail.com>
// Copyright (C) 2019 Yves-Gaël Chény <gitlab@r0b0t.fr>
// Copyright (C) 2019-2021 Oliver Sander <oliver.sander@tu-dresden.de>
// Copyright (C) 2019 <corentinf@free.fr>
// Copyright (C) 2019 Kris Jurka <jurka@ejurka.com>
// Copyright (C) 2019 Sébastien Berthier <s.berthier@bee-buzziness.com>
// Copyright (C) 2020 Stéfan van der Walt <sjvdwalt@gmail.com>
// Copyright (C) 2020 Philipp Knechtges <philipp-dev@knechtges.com>
// Copyright (C) 2021 Diogo Kollross <diogoko@gmail.com>
// Copyright (C) 2021 Vinayak Mehta <vmehta94@gmail.com>
//
// To see a description of the changes please see the Changelog file that
// came with your tarball or type make ChangeLog if you are building from git
//
//========================================================================

#include "config.h"
#include <poppler-config.h>
#ifdef _WIN32
#    include <fcntl.h> // for O_BINARY
#    include <io.h> // for setmode
#endif
#include <cstdio>
#include <cmath>
#include "goo/gmem.h"
#include "goo/GooString.h"
#include "GlobalParams.h"
#include "Object.h"
#include "PDFDoc.h"
#include "PDFDocFactory.h"
#include "splash/SplashBitmap.h"
#include "splash/Splash.h"
#include "splash/SplashErrorCodes.h"
#include "SplashOutputDev.h"
#include "numberofcharacters.h"

#include <pybind11/pybind11.h>
namespace py = pybind11;

static int firstPage = 1;
static int lastPage = 0;
static bool printOnlyOdd = false;
static bool printOnlyEven = false;
static bool singleFile = false;
static bool scaleDimensionBeforeRotation = false;
static double resolution = 300.0;
static double x_resolution = 150.0;
static double y_resolution = 150.0;
static int scaleTo = 0;
static int x_scaleTo = 0;
static int y_scaleTo = 0;
static int param_x = 0;
static int param_y = 0;
static int param_w = 0;
static int param_h = 0;
static bool hideAnnotations = false;
static bool useCropBox = false;
static bool mono = false;
static bool gray = false;
static char sep[2] = "-";
static bool forceNum = false;
static bool png = true;
static bool jpeg = false;
static bool jpegcmyk = false;
static bool tiff = false;
static bool overprint = false;
static bool enableFreeType = true;
static bool fontAntialias = true;
static bool vectorAntialias = true;
static SplashThinLineMode thinLineMode = splashThinLineDefault;
static bool quiet = false;
static bool needToRotate(int angle)
{
    return (angle == 90) || (angle == 270);
}

static auto annotDisplayDecideCbk = [](Annot *annot, void *user_data) { return !hideAnnotations; };

static void savePageSlice(PDFDoc *doc, SplashOutputDev *splashOut, int pg, int x, int y, int w, int h, double pg_w, double pg_h, char *ppmFile)
{
    if (w == 0)
        w = (int)ceil(pg_w);
    if (h == 0)
        h = (int)ceil(pg_h);
    w = (x + w > pg_w ? (int)ceil(pg_w - x) : w);
    h = (y + h > pg_h ? (int)ceil(pg_h - y) : h);
    doc->displayPageSlice(splashOut, pg, x_resolution, y_resolution, 0, !useCropBox, false, false, x, y, w, h, nullptr, nullptr, annotDisplayDecideCbk, nullptr);

    SplashBitmap *bitmap = splashOut->getBitmap();

    if (ppmFile != nullptr) {
        SplashError e;
        e = bitmap->writeImgFile(splashFormatPng, ppmFile, x_resolution, y_resolution);
        if (e != splashOk) {
            fprintf(stderr, "Could not write image to %s; exiting\n", ppmFile);
            exit(EXIT_FAILURE);
        }
    } else {
#ifdef _WIN32
        setmode(fileno(stdout), O_BINARY);
#endif
        bitmap->writeImgFile(splashFormatPng, stdout, x_resolution, y_resolution);
    }
}

void convert(char *pdfFilePath, char *pngFilePath)
{
    GooString *fileName = new GooString(pdfFilePath);
    // https://stackoverflow.com/a/20944858/2780127
    char *ppmFile = pngFilePath;

    SplashColor paperColor;
    SplashOutputDev *splashOut;
    int exitCode;
    int pg, pg_num_len;
    double pg_w, pg_h;

    exitCode = 99;

    if (resolution != 0.0 && (x_resolution == 150.0 || y_resolution == 150.0)) {
        x_resolution = resolution;
        y_resolution = resolution;
    }
    // read config file
    globalParams = std::make_unique<GlobalParams>();

    std::unique_ptr<PDFDoc> doc(PDFDocFactory().createPDFDoc(*fileName));
    delete fileName;

    if (!doc->isOk()) {
        exitCode = 1;
        goto err1;
    }

    if (singleFile && lastPage < 1)
        lastPage = firstPage;
    if (lastPage < 1 || lastPage > doc->getNumPages())
        lastPage = doc->getNumPages();
    if (lastPage < firstPage) {
        fprintf(stderr, "Wrong page range given: the first page (%d) can not be after the last page (%d).\n", firstPage, lastPage);
        goto err1;
    }

    // If our page range selection and document size indicate we're only
    // outputting a single page, ensure that even/odd page selection doesn't
    // filter out that single page.
    if (firstPage == lastPage && ((printOnlyEven && firstPage % 2 == 1) || (printOnlyOdd && firstPage % 2 == 0))) {
        fprintf(stderr, "Invalid even/odd page selection, no pages match criteria.\n");
        goto err1;
    }

    if (singleFile && firstPage < lastPage) {
        if (!quiet) {
            fprintf(stderr, "Warning: Single file will write only the first of the %d pages.\n", lastPage + 1 - firstPage);
        }
        lastPage = firstPage;
    }

    // write PPM files
    if (jpegcmyk || overprint) {
        globalParams->setOverprintPreview(true);
        splashClearColor(paperColor);
    } else {
        paperColor[0] = 255;
        paperColor[1] = 255;
        paperColor[2] = 255;
    }

    splashOut = new SplashOutputDev(mono ? splashModeMono1 : gray ? splashModeMono8 : (jpegcmyk || overprint) ? splashModeDeviceN8 : splashModeRGB8, 4, false, paperColor, true, thinLineMode);

    splashOut->setFontAntialias(fontAntialias);
    splashOut->setVectorAntialias(vectorAntialias);
    splashOut->setEnableFreeType(enableFreeType);
    splashOut->startDoc(doc.get());

    pg_num_len = numberOfCharacters(doc->getNumPages());
    for (pg = firstPage; pg <= lastPage; ++pg) {
        if (printOnlyEven && pg % 2 == 1)
            continue;
        if (printOnlyOdd && pg % 2 == 0)
            continue;
        if (useCropBox) {
            pg_w = doc->getPageCropWidth(pg);
            pg_h = doc->getPageCropHeight(pg);
        } else {
            pg_w = doc->getPageMediaWidth(pg);
            pg_h = doc->getPageMediaHeight(pg);
        }

        if (scaleDimensionBeforeRotation && needToRotate(doc->getPageRotate(pg)))
            std::swap(pg_w, pg_h);

        if (scaleTo != 0) {
            resolution = (72.0 * scaleTo) / (pg_w > pg_h ? pg_w : pg_h);
            x_resolution = y_resolution = resolution;
        } else {
            if (x_scaleTo > 0) {
                x_resolution = (72.0 * x_scaleTo) / pg_w;
                if (y_scaleTo == -1)
                    y_resolution = x_resolution;
            }
            if (y_scaleTo > 0) {
                y_resolution = (72.0 * y_scaleTo) / pg_h;
                if (x_scaleTo == -1)
                    x_resolution = y_resolution;
            }
        }
        pg_w = pg_w * (x_resolution / 72.0);
        pg_h = pg_h * (y_resolution / 72.0);

        if (!scaleDimensionBeforeRotation && needToRotate(doc->getPageRotate(pg)))
            std::swap(pg_w, pg_h);

        savePageSlice(doc.get(), splashOut, pg, param_x, param_y, param_w, param_h, pg_w, pg_h, ppmFile);
    }
    delete splashOut;

    exitCode = 0;
err1:
    ;
}

PYBIND11_MODULE(pdftopng, m) {
    m.doc() = "pdftopng"; // optional module docstring
    m.def("convert", &convert, py::arg("pdf_path"), py::arg("png_path"));
}

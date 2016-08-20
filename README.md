# Overview

This tool is designed to extract analytic data about human-software
interaction from screen captured video of someone playing the game
Contraption Maker.

# Requirements

[GEOS]: http://trac.osgeo.org/geos
[shapely]: https://github.com/Toblerity/Shapely
[tesseract]: https://github.com/tesseract-ocr
[pytesseract]: https://pypi.python.org/pypi/pytesseract/0.1

CMAnalytics requires

  - Python>=2.6 (has not been tested with Python 3)
  - [GEOS] (required by [shapely])
  - [tesseract] (required by [pytesseract])

# Installation

Before installing the python modules, make sure [GEOS] and [tesseract] are installed. Then run

~~~
$ python setup.py install
~~~

# Usage

~~~
$ bin/analyze_video.py movie.mov
~~~

# Current capabilities

At its current state, this tool can

- find a puzzle start frame
- extract a puzzle name
- detect when the 'play' button is pressed
- detect when a help dialog for a part is present and extract the name of the part
- find a puzzle stop frame

This provides information about attempt duration, how often the user
pressed 'play', how frequently they used the help feature and for
which parts they requested help on.

# Theory of operation

Comming soon.

# Dependancies

If you are running Fedora, CentOS, or Ubuntu, there should be binary
packages of GEOS and Tesseract you can install with your distro's
package manager. Otherwise, you will have to compile from source. I
have documented some notes while compiling the dependancies on Solus
OS here, I am still not sure if the trouble I had was due to problem
with my particular Solus install, a bug in the automake scripts for
the project, or just my relative ignorance.

## Tesseract

I had a challenging time building tesseract on Solus OS, I built and installed leptonica following instructions,
but the tesseract configuration script failed the test looking for a specific symbol

comment out lines in configure.ac

~~~
#  AC_CHECK_LIB([lept], [l_generateCIDataForPdf], [],
#               [AC_MSG_ERROR([leptonica library with pdf support (>= 1.71) is missing])])
~~~

and in api/Makefile

~~~
LIBS = -llept -lpng -ljpeg -ltiff -lwebp -lpthread
~~~

note that `l_generateCIDataForPdf` is a valid symbol in the installed leptonica library

~~~
$ nm /usr/local/lib/liblept.so | grep l_generateCIDataForPdf
000000000011a000 T l_generateCIDataForPdf
~~~

so I'm guessing I don't have something configured correctly in the
load library path or related files. This also does not explain why the
other libraries, png, jpeg, etc. were not linked in the generated
Makefile either.

## Python modules

~~~
$ pip install pytesseract pillow matplotlib
~~~

# Todo

- Motion analysis

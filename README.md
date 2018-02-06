This package is for reading and writing Praat TextGrid annotations in Python. It can read TextGrid files that are compatible with the [TextGrid file format](http://www.fon.hum.uva.nl/praat/manual/TextGrid_file_formats.html) specification. It is tested to work with Python 2.7, 3.4, and 3.5.

Usage
-----
The `tgre.py` module docstring shows some usage examples, and the docstrings in `tgre.py` have more detail on functionality.

Installation
------------
The package can be installed from GitHub with this command:

    pip install git+http://github.com/scjs/tgre.git

You can also copy the `tgre` subdirectory into your working directory, or put it in your Python path.

Tests
-----
To run the tests, run `nosetests` from the root directory, or `python setup.py test` to install the test dependencies first.

References
----------
Boersma, Paul & Weenink, David (2016). Praat: doing phonetics by computer [Computer program]. Version 6.0.12, retrieved from http://www.praat.org/

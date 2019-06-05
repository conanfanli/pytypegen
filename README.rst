

.. image:: https://codecov.io/gh/conanfanli/pytypegen/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/conanfanli/pytypegen
   :alt: codecov


.. image:: https://pyup.io/repos/github/conanfanli/pytypegen/shield.svg
   :target: https://pyup.io/repos/github/conanfanli/pytypegen/shield.svg
   :alt: pyup


pytypgen
========

Code generator that converts from Python types (implemented by dataclasses) to TypeScript interfaces

Dependencies
============


* Python 3.7 (need ``dataclass``\ )

Install
=======

``pip install pytypegen``

Development Setup
=================


* Run ``make setup``. This will setup a pre-commit hook which creates README.rst file.
* Run ``pip install -r dev-requirements.txt``\ , preferably in a virtualenv.

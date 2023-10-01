####################
zone3k CSV converter
####################

.. image:: https://badge.fury.io/py/zone3k-csv-converter.svg
    :target: https://badge.fury.io/py/zone3k-csv-converter

.. image:: https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336
    :target: https://pycqa.github.io/isort/

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

.. image:: http://www.mypy-lang.org/static/mypy_badge.svg
    :target: http://mypy-lang.org/

.. image:: https://github.com/whitespy/django-node-assets/actions/workflows/code_quality_check.yml/badge.svg
    :target: https://github.com/whitespy/zone3k-csv-converter/actions/workflows/code_quality_check.yml

Installation
------------

.. code:: bash

    pip install zone3k-csv-converter

Usage
-----

.. code:: bash

    cat /home/user/input.csv | python -m converter --skip 1 --take 2

    # or a shorted variant

    cat /home/user/input.csv | convertcsv -s 1 -t 2

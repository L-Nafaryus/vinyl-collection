vinyl-collection
================
.. contents:: Contents

Main goal is to receive collection from `Discogs <https://www.discogs.com>`_ and save it to local database.

Usage
-----
* Simple:

.. code-block:: bash

   python -m pip install -r requirements
   python -m vinyl pull NAME

* With auto environment:

.. code-block:: bash

   bin/vinyl init
   bin/vinyl run pull NAME
   bin/vinyl clean

For more information use ``--help`` in any place.

Features
--------
* Exporting information from db (currently only pdf; preformatted (not customizable fields)):

.. code-block:: bash

   bin/vinyl run export --fmt pdf

* Configuration file:

.. code-block:: toml

    # config.toml
    db_path = "build/vinyl.db"

    pdf_template = "vinyl/templates/vinyl.tex"
    pdf_path = "build"

    # using discogs client with OAuth authentication (https://www.discogs.com/settings/developers)
    discogs_token = "TOKEN"
    discogs_secret = "SECRET"
    consumer_key = "KEY"
    consumer_secret = "ANOTHER_SECRET"

Dependencies
------------
.. csv-table:: Dependencies
    
    "python", "its a python project (>= 3.9.6)"
    "pdflatex", "for exporting to pdf"

License
-------
``MIT``
See ``LICENSE`` for more information.

coviolations.io web
===================

.. image:: https://travis-ci.org/nvbn/coviolations_web.png
   :alt: Build Status
   :target: https://travis-ci.org/nvbn/coviolations_web
.. image:: https://coveralls.io/repos/nvbn/coviolations_web/badge.png?branch=master
   :alt: Coverage Status
   :target: https://coveralls.io/repos/nvbn/coviolations_web

`See docs on read the docs <https://coviolationsio.readthedocs.org/en/latest/>`_

Installation
------------

Install dependencies:

- for developing:

.. code-block:: bash

    pip install -r requirements/develop.txt

- for production use:

.. code-block:: bash

    pip install -r requirements/production.txt

Copy `coviolations_web/settings/dist.py` to `coviolations_web/settings/local.py` and fill config values.

Create db with:

.. code-block:: bash

    ./manage.py syncdb
    ./manage.py migrate

Download assets with:

.. code-block:: bash

    npm install -g bower
    ./manage.py bower_install

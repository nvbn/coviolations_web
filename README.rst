coviolations.io web
===================

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

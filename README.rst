coviolations.io web
===================

.. image:: https://travis-ci.org/nvbn/coviolations_web.png
   :alt: Build Status
   :target: https://travis-ci.org/nvbn/coviolations_web
.. image:: https://coveralls.io/repos/nvbn/coviolations_web/badge.png?branch=develop
   :alt: Coverage Status
   :target: https://coveralls.io/repos/nvbn/coviolations_web
.. image:: https://goo.gl/72whDy
   :target: http://coviolations.io/projects/nvbn/coviolations_web/

Server side of `coviolations.io <http://coviolations.io>`_

`See docs of server side on read the docs <https://coviolations_web.readthedocs.org/>`_

`See client docs on read the docs <https://coviolationsio.readthedocs.org/en/latest/>`_

Installation
------------

You need `pip`, `npm`, `bower`, `redis` and `mongodb` installed for this instruction.

Install fabric:

.. code-block:: bash

    pip install fabric

Copy `coviolations_web/settings/dist.py` to `coviolations_web/settings/local.py` and fill config values.

And setup for developing with:

.. code-block:: bash

    fab install

Or for production:

.. code-block:: bash

    fab install:production

You can update project with:

.. code-block:: bash

    fab update # or fab update:production

Running
-------

Run http server:

.. code-block:: bash

    ./manage.py runserver

Run sockjs server:

.. code-block:: bash

    ./manage.py runpush

And run rq worker:

.. code-block:: bash

    ./manage.py rqworker

And `open <http://localhost:8000>`_ in browser.

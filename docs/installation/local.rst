*****************
Deploy on local machine
*****************

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


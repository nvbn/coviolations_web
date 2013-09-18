**************
Deploy in production
**************

With puppet
===========

This method recommended and used on `coviolations.io <http://coviolations.io>`_

- Install fabric:

.. code-block:: bash

    pip install fabric

- Copy `puppet/manifests/dist.pp` to `puppet/manifests/private.pp` and fill private data
- Prepare server with:

.. code-block:: bash

    fab prepare_server

You can update to latest version with:

.. code-block:: bash

    fab update_server

Manually
========

- Configure environment - install redis, mongodb, postgresql and what you need.
- Install fabric:

.. code-block:: bash

    pip install fabric

- Install coviolations:

.. code-block:: bash

    fab install:production

You can update to latest version with:

.. code-block:: bash

    fab update:production

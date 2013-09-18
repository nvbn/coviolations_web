*********
Services
*********

Service - function for checking received data from remote and
create :class:`tasks.models.Tasks` object.

For enabling service you need to add it to `settings.SERVICES`, like:

.. code-block:: python

    SERVICES = (
        'services.dummy',
        'services.travis_ci',
        'services.token',
    )


Available services
------------------

.. automodule:: services.dummy
    :members:


.. automodule:: services.token
    :members:


.. automodule:: services.travis_ci
    :members:


Service library
---------------

.. automodule:: services.base
    :members:

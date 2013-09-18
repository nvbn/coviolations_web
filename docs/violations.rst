**********
Violations
**********

Violation - function for parsing raw violation data.

For enabling violation you need to add it to `settings.VIOLATIONS`, like:

.. code-block:: python

    VIOLATIONS = (
        'violations.dummy',
        'violations.pep8',
        'violations.sloccount',
        'violations.py_unittest',
        'violations.pip_review',
        'violations.testem',
    )


Available violations
---------------------

.. automodule:: violations.coverage
    :members:


.. automodule:: violations.dummy
    :members:


.. automodule:: violations.pep8
    :members:


.. automodule:: violations.pip_review
    :members:


.. automodule:: violations.py_unittest
    :members:


.. automodule:: violations.sloccount
    :members:


.. automodule:: violations.testem
    :members:


Violation library
------------------

.. automodule:: violations.base
    :members:

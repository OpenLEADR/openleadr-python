=======
Logging
=======

OpenLEADR uses the standard Python Logging facility. Following the `Python guidelines <https://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library>`_, no default handlers are configured, but you can easily get going if you want to:

Log to standard output
----------------------

To print logs to your standard output, you can use the following convenience method:

.. code-block:: python3

    import openleadr
    import logging
    openleadr.enable_default_logging(level=logging.INFO)

Which is the same as:

.. code-block:: python3

    import logging
    logger = logging.getLogger('openleadr')
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)


Setting the logging level
-------------------------

.. code-block:: python3

    import logging
    logging.getLogger('openleadr')
    logging.setLevel(logging.WARNING)

Redirecting logs to a different file
------------------------------------

To write logs to a file:

.. code-block:: python3

    import logging
    logger = logging.getLogger('openleadr')

    handler = logging.FileHandler('mylogfile.txt')
    logger.addHandler(logger)

More info
---------

Detailed info on logging configuration can be found on `the official Python documentation <https://docs.python.org/3/library/logging.html>`_.
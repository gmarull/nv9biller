NV9 USB Bill Validator Driver
=============================

This is the repository for `nv9biller`, a simple driver for the NV9USB bill
validator using the SSP (unencrypted) protocol. Note that not all features may
be available.

Developer guide
---------------

`pipenv <https://docs.pipenv.org>`_ is used for dependency management, so first
of all make sure you have it installed::

    python -m pip install pipenv

Once you have it, simply run ``pipenv`` on the repository directory to set
everything up::

    pipenv install --dev

and then open a shell on the recently created Python virtual environment::

    pipenv shell

Now you can run any of the examples, e.g.::

    python examples/examples.py COM8

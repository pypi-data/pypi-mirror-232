===========
POP-RELEASE
===========

.. image:: https://img.shields.io/badge/made%20with-pop-teal
   :alt: Made with pop, a Python implementation of Plugin Oriented Programming
   :target: https://pop.readthedocs.io/

.. image:: https://img.shields.io/badge/made%20with-python-yellow
   :alt: Made with Python
   :target: https://www.python.org/


Release facilitator for pop-projects.

About
=====

Pop Release is a simple tool to automate the process of creating a release.
When making POP software releases should be happening very quickly, every
few commits should justify a release.

Since releases happen so frequently, and since they should be executed in
an identical way from project to project, pop-release becomes a simple command
to update the release locally and on pypi.


What is POP?
------------

This project is built with `pop <https://pop.readthedocs.io/>`__, a Python-based
implementation of *Plugin Oriented Programming (POP)*. POP seeks to bring
together concepts and wisdom from the history of computing in new ways to solve
modern computing problems.

For more information:

* `Intro to Plugin Oriented Programming (POP) <https://pop-book.readthedocs.io/en/latest/>`__
* `pop-awesome <https://gitlab.com/saltstack/pop/pop-awesome>`__
* `pop-create <https://gitlab.com/saltstack/pop/pop-create/>`__

Getting Started
===============

Prerequisites
-------------

* Python 3.8+
* git *(if installing from source, or contributing to the project)*

Installation
------------

.. note::

   If wanting to contribute to the project, and setup your local development
   environment, see the ``CONTRIBUTING.rst`` document in the source repository
   for this project.

If wanting to use ``pop-release``, you can do so by either
installing from PyPI or from source.

Install from PyPI
+++++++++++++++++

    If package is available via PyPI, include the directions.

    .. code-block:: bash

        pip install pop-release


Install from source
+++++++++++++++++++

.. code-block:: bash

   # clone repo
   git clone git@gitlab.com/saltstack/pop/pop-release.git
   cd pop-release

   # Setup venv
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -e .

Usage
=====

pop-release can be run several ways.
The traditional method uses a ~/.pypirc config file.
The most powerful and versatile method is to use idem/acct's authentication.

Traditional
-----------

Set up a file called ".pypirc" in your home directory.
Your username will be "__token__" and your password will be an `API token <https://pypi.org/help/#apitoken>`_
With this method you can't choose between the configured profiles.

~/.pypirc

.. code-block::

    [distutils]
    index-servers=
        pypi

    [pypi]
    repository = https://upload.pypi.org/legacy/
    username = __token__
    password = pypi-<pypi_api_token>

With your credentials set up, you can simply run the pop-release command in the root of the directory
that contains your source code.  The only argument you need is a semantic version number.

.. code-block:: bash

    pop-release 1.0.0-alpha

Power User
----------

Using the acct plugin, we can have multiple named profiles.
The "default" and "testing" examples below show the bare minimum of configuration required.
Any options that can be used by a
`twine.settings.Settings <https://github.com/pypa/twine/blob/master/twine/settings.py#L48-L63>`_
object can be included in a twine acct profile.

credentials.yaml

.. code-block:: yaml

    twine:
        default:
            username: __token__
            password: pypi-api-auth-token
            repository_name: pypi
            repository_url: https://upload.pypi.org/legacy/
        testing:
            username: __token__
            password: pypi-testing-api-auth-token
            repository_name: testpypi
            repository_url: https://test.pypi.org/legacy/
        internal:
            sign: True
            sign_with: gpg
            identity:
            username: __token__
            password: pypi-internal-api-auth-token
            comment: My project's private repository
            config_file: ~/.pypirc
            skip_existing: False
            cacert:
            client_cert:
            repository_name: internal_pypi
            repository_url: https://pypi.<my_domain>.com/api

Now encrypt your credentials with `acct`

.. code-block:: bash

    acct encrypt credentials.yaml

If this is the first time you used the command, it will output a fernet key.
Save this key to the environment:

.. code-block:: bash

    export ACCT_KEY="i6KbvytHAYWYiWBV48x5Ao0M3xuP-7Yzyi5K5g4eRQw="

There will also be a new file created called `<credentials_file_name>.fernet`.
Save the full path to this file to your environment:

.. code-block:: bash

    export ACCT_FILE="/home/myuser/.../credentials.yaml.fernet"

Now you can run pop-release using your encrypted credentials.
The profile called "default" will be used implicitly.
You can choose a profile for running pop-release by using the `--acct-profile` option.

PyPi release using the default profile:

.. code-block:: bash

    pop-release 2.0.0

PyPi testing release:

.. code-block:: bash

    pop-release 2.0.0 --acct-profile=testing

Acknowledgements
================

* `Img Shields <https://shields.io>`__ for making repository badges easy.

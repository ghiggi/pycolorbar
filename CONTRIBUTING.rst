Contributors Guidelines
===========================

Hi! Thanks for taking the time to contribute to pycolorbar.

You can contribute in many ways:

- Join the `discussions <https://github.com/ghiggi/pycolorbar/discussions>`__
- Report software `issues <#issue-reporting-guidelines>`__
- Add new colormaps
- Add new colorbars
- ...
- Any code improvements are welcome !

**We Develop with GitHub !**

We use GitHub to host code, to track issues and feature requests, as well as accept Pull Requests.
We use `GitHub flow <https://docs.github.com/en/get-started/quickstart/github-flow>`__.
So all code changes happen through Pull Requests (PRs).


Before adding your contribution, please make sure to take a moment and read through the following documnents :

- `Code of Conduct <https://github.com/ghiggi/pycolorbar/blob/main/CODE_OF_CONDUCT.md>`__
- `Contributing environment setup <#contributing-environment-setup>`__
- `Contributing process <#contributing-process>`__
- `Code review checklist <#code-review-checklist>`__


Issue Reporting
-----------------

-  Always use one of the available `GitHub Issue
   Templates <https://github.com/ghiggi/pycolorbar/issues/new/choose>`__
-  If you do not find the required GitHub Issue Template, please ask for a new template.


Setup the contributor environment
-----------------------------------

**First Time Contributors ?**

Please follow the following steps to install your developing environment :

-  Set up the development environment
-  Install pre-commit hooks

Set up the development environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You will need python to set up the development environment.
See `the installation guide <https://pycolorbar.readthedocs.io/en/latest/installation.html>`__ for further explanations.

Install pre-commit hooks
~~~~~~~~~~~~~~~~~~~~~~~~

After setting up your development environment, install the git pre-commit hook by executing the following command in the repository’s root:

::

   pre-commit install


The pre-commit hooks are scripts executed automatically in every commit
to identify simple code quality issues. When an issue is identified
(the pre-commit script exits with non-zero status), the hook aborts the
commit and prints the error. Currently, pycolorbar only tests that the
code to be committed complies with `black`'s format style, the `ruff` linter and the `codespell` spelling checker.

In case that the commit is aborted, you only need to run the precommit hook again.
This can be done by running   ``black .``,  ``ruff check .`` or ``codespell`` .

.. note::
	To maintain consistency, please use version and configuration defined into `.pre-commit-config.yaml`.



This can also be done with  ``pre-commit run --all-files``. This is recommended since it
indicates if the commit contained any formatting errors (that are automatically corrected).


More info on pre-commit and CI tools are provided in the Code quality and testing section
`Code quality and testing section <https://pycolorbar.readthedocs.io/en/latest/contributors_guidelines.html#code-quality-control>`__



Contributing process
-----------------------

**How to contribute ?**


Here is a brief overview of the steps that each pycolorbar developer must follow to contribute to the repository.

1. Fork the repository.
2. Create a new branch for each contribution.
3. Work on your changes.
4. Test your changes.
5. Push your local changes to your fork repository.
6. Create a new Pull Request in GitHub.


.. image:: /static/collaborative_process.png




1. Fork the repository
~~~~~~~~~~~~~~~~~~~~~~~

Once you have set the development environment (see `Set up the development environment`_), the next step is to create
your local copy of the repository, where you will commit your
modifications. The steps to follow are:

1. Set up Git on your computer

2. Create a GitHub account (if you do not have one)

3. Fork the repository in your GitHub.

4. Clone a local copy of your fork. For example:

::

   git clone https://github.com/<your-account>/pycolorbar.git

Done! Now you have a local copy of the pycolorbar repository.

2. Create a new branch
~~~~~~~~~~~~~~~~~~~~~~~

Each contribution should be made in a separate new branch of your forked repository.
Working on the main branch is reserved for `Core Contributors` only.
Core Contributors are developers that actively work and maintain the repository.
They are the only ones who accept Pull Requests and push commits directly to the pycolorbar repository.

For more information on how to create and work with branches, see
`“Branches in a
Nutshell” <https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell>`__
in the Git documentation.

Please define the name of your branch based on the scope of the contribution. Try to strictly stick to the following guidelines:

-  If you add some colormaps, use : ``add-colormaps-<name>``
-  If you fix a bug: ``bugfix-<some_key>-<word>``
-  If you improve the documentation: ``doc-<some_key>-<word>``
-  If you add a new feature: ``feature-<some_key>-<word>``
-  If you refactor some code: ``refactor-<some_key>-<word>``
-  If you optimize some code: ``optimize-<some_key>-<word>``

For example, if you are adding new colormaps, you can create a new branch with the following command:

::

   git checkout -b add-colormaps-<name>


3. Work on your changes
~~~~~~~~~~~~~~~~~~~~~~~~~~


We follow the `PEP 8 <https://pep8.org/>`__ style guide for python code.
Another relevant style guide can be found in the `The Hitchhiker's Guide to Python <https://docs.python-guide.org/writing/style/>`__.

To ensure a minimal style consistency, we use `black <https://black.readthedocs.io/en/stable/>`__ to auto-format the source code.
The `black` configuration used in the pycolorbar project is
defined in the `pyproject.toml <https://github.com/ghiggi/pycolorbar/blob/main/pyproject.toml>`__ ,
and it is automatically detected by `black` (see above).



**Docstrings**

Every module, function, or class must have a docstring that describes its
purpose and how to use it. The docstrings follows the conventions
described in the `PEP 257 <https://www.python.org/dev/peps/pep-0257/#multi-line-docstrings>`__
and the `Numpy’s docstrings
format <https://numpydoc.readthedocs.io/en/latest/format.html>`__.

Here is a summary of the most important rules:

-  Always use triple quotes for doctrings, even if it fits a single
   line.

-  For one-line docstring, end the phrase with a period.

-  Use imperative mood for all docstrings (``“””Return some value.”””``)
   rather than descriptive mood (``“””Returns some value.”””``).

Here is an example of a docstring:

::

    def adjust_lag2_corrcoef1(gamma_1, gamma_2):
       """
       A simple adjustment of lag-2 temporal autocorrelation coefficient to
       ensure that the resulting AR(2) process is stationary when the parameters
       are estimated from the Yule-Walker equations.

       Parameters
       ----------
       gamma_1 : float
         Lag-1 temporal autocorrelation coefficient.
       gamma_2 : float
         Lag-2 temporal autocorrelation coefficient.

       Returns
       -------
       out : float
         The adjusted lag-2 correlation coefficient.
       """


If you are using VS code, you can install the  `autoDocstring <https://marketplace.visualstudio.com/items?itemName=njpwerner.autodocstring>`_
extension to automatically create such preformatted docstring.

You should configure VS code as follow :


.. image:: /static/vs_code_settings.png


The convention we adopt for our docstrings is the numpydoc string convention.


Code quality control
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


To maintain a high code quality, `Black`, `Ruff` and `codespell` are defined in the
`.pre-commit-config.yaml <https://github.com/ghiggi/pycolorbar/blob/main/.pre-commit-config.yaml>`_ file.
These tools are run for every Pull Request on GitHub and can also be run locally.


+-----------------------------------------------------------------------------------------------+------------------------------------------------------------------+------------+-------+
|  Tool                                                                                         | Aim                                                              | pre-commit | CI/CD |
+===============================================================================================+==================================================================+============+=======+
| `Black <https://black.readthedocs.io/en/stable/>`__                                           | Python code formatter                                            | 👍         | 👍    |
+-----------------------------------------------------------------------------------------------+------------------------------------------------------------------+------------+-------+
| `Ruff  <https://github.com/charliermarsh/ruff>`__                                             | Python linter                                                    | 👍         | 👍    |
+-----------------------------------------------------------------------------------------------+------------------------------------------------------------------+------------+-------+
| `Codespell  <https://github.com/codespell-project/codespell>`__                               | Spelling checker                                                 | 👍         | 👍    |
+-----------------------------------------------------------------------------------------------+------------------------------------------------------------------+------------+-------+



**pre-commit**

To run pre-commit (black + Ruff) locally :

.. code-block:: bash

   pre-commit run --all-files


This is recommended since it indicates if the commit contained any formatting errors (that are automatically corrected).



**Black**

To run `Black` locally :

.. code-block:: bash

	black .



.. note::
	To maintain consistency, make sure to stick to the version defined in the `.pre-commit-config.yaml <https://github.com/ghiggi/pycolorbar/blob/main/.pre-commit-config.yaml>`_ file. This version will be used in the CI.



**Ruff**

To run `Ruff` locally :

.. code-block:: bash

	ruff check .


.. note::
	To maintain consistency, make sure to stick to the version and the rule configuration defined in the `.pre-commit-config.yaml <https://github.com/ghiggi/pycolorbar/blob/main/.pre-commit-config.yaml>`_ file. This version will be used in the CI.



**Codespell**

To run `Codespell` locally :

.. code-block:: bash

	codespell


.. note::
	To maintain consistency, make sure to stick to the version and the rule configuration defined in the `.pre-commit-config.yaml <https://github.com/ghiggi/pycolorbar/blob/main/.pre-commit-config.yaml>`_ file. This version will be used in the CI.


In the table below, some CI tools are mentioned for your information, but does not need to be installed on your computer.
They are automatically run when you push your changes to the main repository via a GitHub Pull Request.


+----------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------+
| Tool                                               | Aim                                                                                                                                 |
+====================================================+=====================================================================================================================================+
| `pre-commit.ci <https://pre-commit.ci/>`__         | Run pre-commit (as defined in `.pre-commit-config.yaml <https://github.com/ghiggi/pycolorbar/blob/main/.pre-commit-config.yaml>`__) |
+----------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------+
| `CodeBeat <https://codebeat.co/>`__                | Automated code review and analysis tools                                                                                            |
+----------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------+
| `CodeScene <https://codescene.com/>`__             | Automated code review and analysis tools                                                                                            |
+----------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------+
| `CodeFactor <https://www.codefactor.io/>`__        | Automated code review and analysis tools                                                                                            |
+----------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------+
| `Snyk Code <https://snyk.io/product/snyk-code/>`__ | Automated code security checks                                                                                                      |
+----------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------+



4. Code testing
~~~~~~~~~~~~~~~~


Every code change must be tested !




**Pytest**

pycolorbar tests are written using the third-party `pytest <https://docs.pytest.org>`_ package.



The tests located in the ``/pycolorbar/tests`` directory are used to test various functions of the code and are automatically run
when changes are pushed to the main repository through a GitHub Pull Request.

.. code-block:: bash

	pytest pycolorbar/tests


The Continuous Integration (CI) on GitHub runs tests and analyzes code coverage. The following tools are used:


+-----------------------------------------------------------------------------------------------+------------------------------------------------------------------+
|  Tool                                                                                         | Aim                                                              |
+===============================================================================================+==================================================================+
| `Pytest  <https://docs.pytest.org>`__                                                         | Execute unit tests and functional tests                          |
+-----------------------------------------------------------------------------------------------+------------------------------------------------------------------+
| `Coverage <https://coverage.readthedocs.io/>`__                                               | Measure the code coverage of the project's unit tests            |
+-----------------------------------------------------------------------------------------------+------------------------------------------------------------------+
| `CodeCov    <https://about.codecov.io/>`__                                                    | Uses the "coverage" package to generate a code coverage report.  |
+-----------------------------------------------------------------------------------------------+------------------------------------------------------------------+
| `Coveralls    <https://coveralls.io/>`__                                                      | Uses the "coverage" to track the quality of your code over time. |
+-----------------------------------------------------------------------------------------------+------------------------------------------------------------------+


5. Push your changes to your fork repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

During this process, pre-commit hooks will be run. Your commit will be
allowed only if quality requirements are fulfilled.

If you encounter errors, Black and Ruff can be run using the following command:

::

   pre-commit run --all-files

We follow a `commit message convention <https://www.conventionalcommits.org/en/v1.0.0/>`__, to have consistent git messages.
The goal is to increase readability and ease of contribution.



6. Create a new Pull Request in GitHub.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once your code has been uploaded into your pycolorbar fork, you can create
a Pull Request (PR) to the pycolorbar main branch.

**Recommendation for the Pull Request**

-  Add screenshots or GIFs for any UI changes. This will help the person reviewing your code to understand what you have changed and how it
   works.

-  Please use the pertinent template for the Pull Request, and fill it out accurately.
-  It is OK to have multiple small commits as you work on the PR - GitHub  will automatically squash it before merging.
-  If adding a new feature:

   -  Add accompanying test case.
   -  Provide a convincing reason to add this feature. Ideally, you should open a suggestion issue first and have it approved before working on it.
   -  Optionally, you can also present your issue in the repository `Discussions <https://github.com/ghiggi/pycolorbar/discussions>`__.

-  If fixing bug:

   -  If you are resolving a special issue, add ``(fix #xxxx)`` in your PR title for a better release log. For example: ``Update L0 encoding compression (fix #3899)``.
   -  Provide a detailed description of the bug in the PR.
   -  Add appropriate test coverage if applicable.



.. _section-1:

Code review checklist
---------------------

-  Ask two people to review your code:

   -  a person who knows the domain well and can spot bugs in the business logic;
   -  an expert in the technologies you are using who can help you improve the code quality.

-  When you are done with the changes after a code review, do another  self review of the code and write a comment to notify the reviewer,
   that the Pull Request is ready for another iteration.
-  Resolve all the review comments, making sure they are all addressed before another review iteration.
-  Make sure you do not have similar issues anywhere else in your Pull Request.
-  If you are not going to follow a code review recommendations, please add a comment explaining why you think the reviewer suggestion is not relevant.
-  Avoid writing comment like “done” of “fixed” on each code review comment.
   Reviewers assume you will do all suggested changes, unless you have a reason not to do some of them.
-  Sometimes it is okay to postpone changes — in this case you will need to add a ticket number to the Pull Request and to the code itself.

.. _section-2:


Credits
-------

Thank you to all the people who have already contributed to pycolorbar repository!

If you have contributed colormaps and/or code to pycolorbar, add your name to the `AUTHORS.md <https://github.com/ghiggi/pycolorbar/blob/main/AUTHORS.md>`__ file.

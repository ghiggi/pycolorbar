========================
Maintainers Guidelines
========================


The section is dedicated to the pycolorbar core developers (maintainers).


List of the core contributors
=================================

* Current Release Manager : Ghiggi Gionata
* Testing Team : Ghiggi Gionata



Versions guidelines
========================

pycolorbar uses `Semantic <https://semver.org/>`_ Versioning. Each release is associated with a git tag of the form X.Y.Z.

Given a version number in the MAJOR.MINOR.PATCH (eg., X.Y.Z) format, here are the differences in these terms:

- MAJOR version - make breaking/incompatible API changes
- MINOR version - add functionality in a backwards compatible manner. Adding new reader
- PATCH version - make backwards compatible bug fixes


Breaking vs. non-breaking changes
-----------------------------------

Since pycolorbar is used by a broad ecosystem of both API consumers and implementers, it needs a strict definition of what changes are “non-breaking” and are therefore allowed in MINOR and PATCH releases.

In the pycolorbar specifications, a breaking change is any change that requires either consumers or implementers to modify their code for it to continue to function correctly.

Examples of breaking changes include:

- Renaming a pycolorbar colormap.
- Changing the input/output format/structure of pycolorbar configuration YAML file.
- Adding new functionalities to the pycolorbar that affect the behavior of the software directly.
- Modify the argument name of a pycolorbar function.

Examples of non-breaking changes include :

- Fix a bug.
- Adding new colormaps
- Adding new features (i.e. Norm)
- Adding new functionalities to the pycolorbar API that do not affect the behavior of the API directly.
- Updating the documentation.
- Internal function refactoring that does not affect the behavior of the software directly.


One implication of this policy is that clients should be prepared to ignore the presence of unexpected fields in responses and unexpected values for enums. This is necessary to preserve compatibility between PATCH versions within the same MINOR version range, since optional fields and enum values can be added as non-breaking changes.


Ongoing version support
-----------------------------------

pycolorbar major releases aims to move the community forward, focusing on specifications stabilization and major feature additions, rather than backwards-compatibility. pycolorbar minor releases will be backwards compatible. We strongly recommend adopting the latest release of pycolorbar into production within 6 months for major releases, and 4 months for minor releases.

The maintaners do their best but does not guarantee any period of support or maintenance.

Releases that are 2 years or older may be considered as deprecated.

Refer to the list of Recommended Releases to see current releases and more details.


Documentation pipeline
========================

pycolorbar's documentation is built using Sphinx. All documentation lives in the ``docs/`` directory of the project repository.


Manual documentation creation
-----------------------------

After editing the source files, the documentation can be generated locally:


.. code-block:: bash

	cd docs
	make html


The output of the previous command should be checked for warnings and errors. If the code is changed (new functions or classes), then the pycolorbar documentation files located in ``docs/source/api`` are automatically regenerated when building the documentation using the command above.


Automatic (GitHub) documentation creation
------------------------------------------


One webhook is defined in the repository to trigger the publication process to readthedoc.io.

This webhook is linked to the pycolorbar core developer.

.. image:: /static/documentation_pipepline.png

Ghiggi Gionata owns the `ReadTheDoc <https://readthedocs.org/>`__ account.


Package releases pipeline
============================

One  `GitHub Action <https://github.com/ghiggi/pycolorbar/actions>`_ is defined to trigger the packaging and the upload on `pypi.org <https://pypi.org/project/pycolorbar/>`_.

.. image:: /static/package_pipeline.png

The `PyPi <https://pypi.org/>`__ project is shared between the core contributors.



Reviewing process
============================


The main branch is protected and requires at least one review before merging.

The review process is the following:

#. A PR is opened by a contributor
#. The CI pipeline is triggered and the status of the tests is reported in the PR.
#. A core contributor reviews the PR and request changes if needed.
#. The contributor updates the PR according to the review.
#. The core contributor reviews the PR again and merge it if the changes are ok.



Continuous integration (CI) testing tools
===========================================

Currently, on each Pull Request, GitHub Actions are configured as follow:


+----------------------------------------------------------------------------------------------------+------------------------------------------------------------------+----------------------------------------------------------------------------------------------+
|  Tools                                                                                             | Aim                                                              | Project page                                                                                 |
+====================================================================================================+==================================================================+==============================================================================================+
| `Pytest  <https://docs.pytest.org>`__                                                              | Execute unit tests and functional tests                          |                                                                                              |
+----------------------------------------------------------------------------------------------------+------------------------------------------------------------------+----------------------------------------------------------------------------------------------+
| `Black <https://black.readthedocs.io/en/stable/>`__                                                | Python code formatter                                            |                                                                                              |
+----------------------------------------------------------------------------------------------------+------------------------------------------------------------------+----------------------------------------------------------------------------------------------+
| `Ruff  <https://github.com/charliermarsh/ruff>`__                                                  | Python linter                                                    |                                                                                              |
+----------------------------------------------------------------------------------------------------+------------------------------------------------------------------+----------------------------------------------------------------------------------------------+
| `pre-commit.ci   <https://pre-commit.ci/>`__                                                       | Run pre-commit as defined in `.pre-commit-config.yaml <https://github.com/ghiggi/pycolorbar/blob/main/.pre-commit-config.yaml>`_                                  |
+----------------------------------------------------------------------------------------------------+------------------------------------------------------------------+----------------------------------------------------------------------------------------------+
| `Coverage   <https://coverage.readthedocs.io/>`__                                                  | Measure the code coverage of the project's unit tests            |                                                                                              |
+----------------------------------------------------------------------------------------------------+------------------------------------------------------------------+----------------------------------------------------------------------------------------------+
| `CodeCov    <https://about.codecov.io/>`__                                                         | Uses the "coverage" package to generate a code coverage report.  | `pycolorbar  <https://app.codecov.io/gh/ghiggi/pycolorbar>`__                                    |
+----------------------------------------------------------------------------------------------------+------------------------------------------------------------------+----------------------------------------------------------------------------------------------+
| `Coveralls    <https://coveralls.io/>`__                                                           | Uses the "coverage" to track the quality of your code over time. | `pycolorbar  <https://coveralls.io/github/ghiggi/pycolorbar>`__                                  |
+----------------------------------------------------------------------------------------------------+------------------------------------------------------------------+----------------------------------------------------------------------------------------------+
| `CodeBeat      <https://codebeat.co/>`__                                                           | Automated code review and analysis tools                         | `pycolorbar <https://codebeat.co/projects/github-com-ltelab-pycolorbar-main/security_issues>`__  |
+----------------------------------------------------------------------------------------------------+------------------------------------------------------------------+----------------------------------------------------------------------------------------------+
| `CodeScene <https://codescene.com/>`__                                                             | Automated code review and analysis tools                         | `pycolorbar <https://codescene.io/projects/36773>`__                                           |
+----------------------------------------------------------------------------------------------------+------------------------------------------------------------------+----------------------------------------------------------------------------------------------+
| `CodeFactor <https://www.codefactor.io/>`__                                                        | Automated code review and analysis tools                         | `pycolorbar <https://www.codefactor.io/repository/github/ghiggi/pycolorbar>`__                   |
+----------------------------------------------------------------------------------------------------+------------------------------------------------------------------+----------------------------------------------------------------------------------------------+
| `Snyk Code <https://snyk.io/product/snyk-code/>`__                                                 | Automated code security checks                                   | `pycolorbar <https://app.snyk.io/org/ghiggi/project/57219345-56bd-4fbb-b6eb-2a8d955f9924>`__   |
+----------------------------------------------------------------------------------------------------+------------------------------------------------------------------+----------------------------------------------------------------------------------------------+

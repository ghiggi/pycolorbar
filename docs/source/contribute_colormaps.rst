======================
Contribute Colormaps
======================

Do you want to contribute your own colormap to the pycolorbar archive ? Great! You are in the right place !

Here below we provide a detailed description of the steps to follow to contribute your colormap configuration to pycolorbar:

.. contents::
   :depth: 1
   :local:

Before going down the road, please also have a look at the `Contributors Guidelines <contributors_guidelines.html>`_.

.. _step1:

Step 1: Fork, clone and install the pycolorbar repository
--------------------------------------------------------------

1. Go to the `pycolorbar repository <https://github.com/ghiggi/pycolorbar>`__, fork the repository on your GitHub account and then clone the forked repository:

   .. code:: bash

      git clone https://github.com/<your_username>/pycolorbar.git

2. Go inside the ``pycolorbar`` directory where you have cloned the repository and install the pycolorbar python package in editable mode
   following the guidelines reported in the :ref:`Installation for Contributors <installation_contributor>`.

3. Create a new branch:

   .. code:: bash

      git checkout -b "add-colormaps-<name>"


4. Set the remote upstream branch:

   .. code:: bash

      git push --set-upstream origin "add-colormaps-<name>"

5. Every time you will now ``git add *`` and ``git commit -m <describe-your-change>`` your changes, you will be able to push them to your forked repository with:

   .. code:: bash

      git push

6. When you want to show your changes to the pycolorbar maintainers, you will need to open a Pull Request.
   To do so, go to the `GitHub pycolorbar repository <https://github.com/ghiggi/pycolorbar>`__, open the Pull Request and ask for a review.

   For more information on GitHub Pull Requests, read the
   `"Create a pull request documentation" <https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request>`__.

   If you struggle with this process, do not hesitate to raise an `issue <https://github.com/ghiggi/pycolorbar/issues/new/choose>`__
   or ask in the `pycolorbar Slack Workspace <https://join.slack.com/t/pycolorbar/shared_invite/zt-2bxdsywo3-368GbufPyb8vNJ1GC9aT3g>`__ so that we can help !


.. _step2:

Step 2: Define and save the colormap configurations
----------------------------------------------------

To start defining your colormap configuration YAML files, please refers
to the :doc:`Introduction to Univariate Colormaps <tutorials/Introduction_univariate_colormaps>`
documentation.

Consider adding relevant colormap categories within the `category` field of the `auxiliary` subdictionary.
These categories help differentiate between colormaps based on:

- the type of colormap: `cyclic`, `diverging`, `sequential`, `qualitative`, `perceptual`.
- the variables for which the colormap is commonly used (i.e. elevation, bathymetry, precipitation, temperature, etc.).
- the author or source agency of the colormap (i.e. `brewer`, `crameri`, `meteoswiss`, `nasa`, etc.).

Additionally, in the `auxiliary` subdictionary, you can specify custom fields such
as `comments`, `references`, `url`, `author`, `license`.

Once your colormap configurations are finalized, save the configuration YAML files in the `pycolorbar/etc/colormaps` directory.

Before proceeding, please review the existing directories within `pycolorbar/etc/colormaps`.
If it seems appropriate, create a new directory and place your colormap configuration YAML files inside it.

.. note:: Guidelines for the naming of the colormap configuration YAML files:

   * The colormap name must not end with `_r`.

   * Usage of dash ( - ) and underscore ( _ ) is allowed.

   * If you're adding colormap configurations of a specific author (i.e. `brewer`, `crameri`), consider naming the new directory after the original author.

   * If you're adding colormap configurations of a specific variable (i.e. `precipitation`, `temperature`), consider naming the new directory after the variable.


.. _step3:

Step 3: Test the configurations validity
------------------------------------------

When you are done with the editing your colormaps YAML files, please verify that
the colormap configurations you added are valid.

To test the validity of the colormap configurations, you can execute the following command in your terminal:

.. code:: bash

   python -c "import pycolorbar; pycolorbar.check_colormap_archive()"

or alternatively you can run the `check_colormap_archive` function in python:

.. code:: python

    import pycolorbar

    pycolorbar.check_colormap_archive()

If these commands do not raise errors, congratulations ! Your colormap configurations are valid.

.. _step5:

Step 4: Submit your colormaps
-------------------------------

You are now ready to open a Pull Request and submit your colormaps to the pycolorbar archive.

Your Pull Requests will be merged as soon as a pycolorbar maintainer can check your work,
and the colormap will be available to the pycolorbar community.

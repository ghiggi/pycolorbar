======================
Contribute Colormaps
======================

Do you want to contribute your own colormap to to pycolorbar ? Great! You are in the right place !

The data contributor is asked to perform the following 4 tasks:

-  a
-  b
-  c
-

Before proceeding, you need to start thinking about the ``<DATA_SOURCE>`` and ``<CAMPAIGN_NAME>`` names of your stations.
The name you adopt for the ``<DATA_SOURCE>`` and ``<CAMPAIGN_NAME>`` will be used to define:

-  the name of the directory where the colormaps YAML files will be stored in the pycolorbar archive.
-  the name of the colormaps you want to contribute.


.. note:: Guidelines for the naming of the colormaps:

   * The colormap name must not end with `_r`.

   * Usage of dash ( - ) and underscore ( _ ) is allowed.

   * Consider to add the name of source package or colormap collection as a prefix following the pattern `<package_name>.<colormap_name>`

   * Avoid the use of dots ( . ) if not for identify the source package or colormap collection.


Here below we provide a detailed description of the steps to follow to contribute your data to pycolorbar:

* `Step 1 <#step1>`_: Fork and download the pycolorbar repository
* `Step 2 <#step2>`_: Fork and install the pycolorbar python package in editable mode
* `Step 3 <#step3>`_: Add the colormap YAML files pycolorbar/etc/colormaps
* `Step 4 <#step4>`_: Test the colormaps can be retrieved using pycolorbar
* `Step 5 <#step5>`_: Open a Pull Request to submit your colormaps !

Before going down the road, please also have a look at the `Contributors Guidelines <contributors_guidelines.html>`_.

.. _step1:

Step 1: Fork and download the pycolorbar Metadata Archive
--------------------------------------------------------------

1. Go to the `pycolorbar repository <https://github.com/ghiggi/pycolorbar>`__, fork the repository on your GitHub account and then clone the forked repository:

   .. code:: bash

      git clone https://github.com/<your_username>/pycolorbar.git

2. Go inside the ``pycolorbar`` directory where you have cloned the repository:

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

Step 2: Install pycolorbar in editable mode
-------------------------------------------

In order to contribute a reader to pycolorbar, it is necessary that you follow the steps detailed here below
to install your local version of the `pycolorbar python package  <https://github.com/ghiggi/pycolorbar>`__ in editable mode.


1. Go to the `pycolorbar python package repository <https://github.com/ghiggi/pycolorbar>`__, fork the repository on your GitHub account and then clone the forked repository:

   .. code:: bash

      git clone https://github.com/<your_username>/pycolorbar.git

2. Go inside the ``pycolorbar`` directory where you have cloned the repository

3. Create a new branch where you will add your colormaps:

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


7. Finally, install the pycolorbar python package in editable mode using:

   .. code:: bash

      pip install -e .


.. _step3:

Step 3: Add colormaps YAML files
--------------------------------------------

TODO: Add the description of the steps to follow to add the colormap YAML files to the pycolorbar/etc/colormaps directory.

.. code:: python

    import pycolorbar

    base_dir = "<path_to>/pycolorbar/pycolorbar"
    pycolorbar.colormaps.add_cmap_dict()
    pycolorbar.colormaps.validate()


The YAML file can contain auxiliary information related to the colormap.

The optional auxiliary metadata keys are:

* the ``category``


TODO: check perceptual, check category, check_not_exists_already ...


.. _step4:

Step 4: Test colormaps YAML files
--------------------------------------

When you are done with the editing your colormaps YAML files, please run the
following command to check that the specified colormaps YAML files are valid:

.. code:: bash

   pycolorbar_test_colormaps




.. _step5:

Step 5: Open a Pull Request to submit your colormaps !
--------------------------------------------------------------

 If everything looks as expected ... congratulations, you made it !!!

Your Pull Requests will be merged as soon as a pycolorbar maintainer can check your work, and the data and reader will be available to the pycolorbar community.

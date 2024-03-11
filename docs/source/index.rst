.. d documentation master file, created by
   sphinx-quickstart on Wed Jul 13 14:44:07 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to pycolorbar !
========================


Motivation
===========

The creation of the pycolorbar software is driven by the need for a versatile and intuitive tool that simplifies the process of generating consistent and aesthetically pleasing colorbars for scientific visualization.

This need arises from the challenges faced by researchers and data scientists in representing complex data sets clearly and effectively.

In the realm of data visualization, color plays a crucial role in the interpretation of multidimensional data.
It conveys information about value ranges and data distribution, which is essential for drawing meaningful conclusions.
However, creating colorbars that are both informative and visually appealing can be a time-consuming task, often requiring manual tweaking and a deep understanding of the underlying plotting libraries.

**pycolorbar** is designed to address these challenges by providing a modular and configurable system that allows users to define color maps and colorbar characteristics in a simple, reusable format. The software aims to streamline the process of customizing color schemes for various data ranges and types, making it easier for users to create colorbars that are tailored to their specific needs.

The motivation behind **pycolorbar** is also to foster consistency across different visualizations. By allowing users to register and reuse colorbar configurations, the software ensures that a set of plots within the same project or across collaborative works maintains uniformity in color representation. This consistency is key for comparative analysis and for maintaining a professional standard in published materials.

Moreover, **pycolorbar** is developed with extensibility in mind.
It supports a range of color spaces and provides tools for validating the color configurations, ensuring that users can expand the software's capabilities as new visualization challenges arise.

In summary, the motivation for creating pycolorbar is to empower users to craft clear, informative, and beautiful visual representations of their data with ease and confidence, enhancing the communication of scientific findings through effective visualization.

Software
===========

The software currently enable to:

- define colormaps in YAML files
- define colorbars settings in YAML files
- to plot univariate colorbars
- to plot bivariate colorbars
- to plot trivariate colorbars
- to plot circular colorbars


Community
===========

If you are eager to contribute or simply curious about what we do, please do not hesitate to reach out.

Feel warmly invited to join the `pycolorbar Slack Workspace <https://join.slack.com/t/pycolorbar/shared_invite/zt-2bxdsywo3-368GbufPyb8vNJ1GC9aT3g>`__
and say hi !


Documentation
=============

.. toctree::
   :maxdepth: 2

   installation
   quick_start
   contribute_colormaps
   contributors_guidelines
   maintainers_guidelines
   authors


.. toctree::
   :maxdepth: 2

   pycolorbar API <api/modules>





Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

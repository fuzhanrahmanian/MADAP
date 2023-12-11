.. MADAP documentation master file, created by
   sphinx-quickstart on Mon Jul 25 21:56:34 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to MADAP's documentation!
=================================

   This documentation is generated from the MADAP source code. It is
   intended to be used by developers and users of MADAP.


What is MADAP?
--------------

This is MADAP, a software package for the analysis of electrochemical data.
This package consists of 3 main classes for analysis:

-  Voltammetry
-  Impedance spectroscopy
-  Arrhenius

This package allows user to upload any common file format of data and
the select the data of choice. The user can use to scientifically plot
and get correspondence analysis from each procedure (i.e. by calling
“eis_analysis” , Nyquist, bode as well as the correspondence equivalent
circuit and its parameters will be drawn). This package can be installed
via pip/conda and can be utilized with a GUI, command line or just
directly importing the module in a python script. For more information,
checkout the `pypi <https://pypi.org/project/MADAP/>`__ package page and
the `github <https://github.com/fuzhanrahmanian/MADAP>`__ page where you
can find the source code and releases.



.. toctree::
   :maxdepth: 2
   :caption: Usage:

   source/usage/usage

.. toctree::
   :maxdepth: 6
   :caption: Packages:

   source/generated_arrhenius/modules
   source/generated_impedance/modules
   source/generated_voltammetry/modules

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

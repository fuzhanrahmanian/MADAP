MADAP
~~~~~

Modular and Autonomous Data Analysis Platform (MADAP) is a
well-documented python package which can be used for electrochmeical
data analysis.

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
directly importing the module in a python script.

Documentation
~~~~~~~~~~~~~

A documentation for the implementation and use of MADAP can be found
`here <https://fuzhanrahmanian.github.io/MADAP/>`__


Installation
~~~~~~~~~~~~

MADAP can be installed via pip:

.. code:: bash

   pip install madap


Usage
~~~~~

MADAP can be used in a python script as follows:

.. code:: python

   from madap import MADAP

   madap = MADAP()
   madap.load_data('data.csv')
   madap.voltammetry_analysis()
   madap.eis_analysis()
   madap.arrhenius_analysis()

MADAP can also be used via command line:

.. code:: bash

   madap -f data.csv -v -e -a

MADAP can also be used via a GUI:

.. code:: bash

   python -m madap_gui


License
~~~~~~~

MADAP is licensed under the MIT license. See the LICENSE file for more
details.


Citation
~~~~~~~~

If you use MADAP in your research, please cite the following paper:


References
~~~~~~~~~~

This package is based relies on the following packages:
-  Impedance GitHub repository by Matthew D. Murbach and Brian Gerwe and Neal Dawson-Elli and Lok-kun Tsui: `link https://github.com/ECSHackWeek/impedance.py`

.. image:: logo.png
    :align: center

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

   pip install MADAP


Usage
~~~~~

A brief tutorial video of the basic of MADAP usage can found  `here <https://youtu.be/nL-eJpb1AxI>`_. 

MADAP can be used in a python script as follows: 

.. code:: python

    from madap.echem.arrhenius import arrhenius
    from madap.echem.e_impedance import e_impedance
    from madap.data_acquisition import data_acquisition as da


    # Load the data
    data = da.acquire_data('data.csv')
    # Define the desired plots for Arrhenius analysis
    plots_arr = ["arrhenius", "arrhenius_fit"]
    # Define the desired plots for impedance analysis
    plots_eis = ["nyquist", "nyquist_fit", "bode", "residual"]
    # Define a save location#
    save_dir = "/results"

    ### Arrhenius
    # Instantiate the Arrhenius class for analysis (column names do not have to match exactly, this is just an example)
    Arr = arrhenius.Arrhenius(da.format_data(data["temperature"], da.format_data(data["conductivity"])))
    # Perform analysis and plotting
    Arr.perform_all_actions(save_dir, plots = plots_arr)

    ### Impedance
    # Initialize the Impedance class for analysis (column names do not have to match exactly, this is just an example)
    Im = e_impedance.EImpedance(da.format_data(data["freq"]), da.format_data(data["real"]), da.format_data(data["img"]))
    # Initialis the EIS procedure. The initial value is the initial guess for the equivalent circuit (can also be left empty)
    Eis  = e_impedance.EIS(Im, suggested_circuit = "R0-p(R1,CPE1)",initial_value =[860, 3e+5, 1e-09, 0.90])
    # Analyze the data
    Eis.perform_all_actions(save_dir, plots = plots_eis)

    # More usages and options can be found in the documentation.

MADAP can also be used via command line:

.. code:: bash

   python -m madap_cli --file <path_to_file> --procedure <procedure> --results <path_to_results> --header_list <header_list> --plot <list_of_plots>

MADAP can also be used via a GUI:

.. code:: bash

   python -m madap_gui


License
~~~~~~~

MADAP is licensed under the MIT license. See the LICENSE file for more
details.


Citation
~~~~~~~~

If you use MADAP in your research, please cite this GitHub repository https://github.com/fuzhanrahmanian/MADAP.

.. image:: https://zenodo.org/badge/494354435.svg
   :target: https://zenodo.org/badge/latestdoi/494354435


References
~~~~~~~~~~

This package is based relies on the following packages and papers:
- Impedance GitHub repository by Matthew D. Murbach and Brian Gerwe and Neal Dawson-Elli and Lok-kun Tsui: `link <https://github.com/ECSHackWeek/impedance.py>`__
- A Method for Improving the Robustness of linear Kramers-Kronig Validity Tests DOI: https://doi.org/10.1016/j.electacta.2014.01.034

Acknowledgement
~~~~~~~~~~~~~~~

This project has received funding from the European Union’s [Horizon 2020 research and innovation programme](https://ec.europa.eu/programmes/horizon2020/en) under grant agreement [No 957189](https://cordis.europa.eu/project/id/957189). The project is part of BATTERY 2030+, the large-scale European research initiative for inventing the sustainable batteries of the future.

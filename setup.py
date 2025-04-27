#!/usr/bin/env python

"""The setup script."""

from setuptools import find_packages, setup

with open('README.rst', encoding="utf-8") as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst', encoding="utf-8") as history_file:
    history = history_file.read()

requirements = ["attrs==21.4.0",
        "matplotlib",
        "numpy",
        "pandas",
        "PySimpleGUI",
        "pytest",
        "scikit_learn",
        "ruptures",
        "impedance==1.4.1"]

test_requirements = ['pytest>=3', ]

setup(
    author="Fuzhan Rahmanian",
    author_email='fuzhanrahmanian@gmail.com',
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Scientific/Engineering :: Chemistry',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Scientific/Engineering :: Visualization',
    ],
    description="This is MADAP, a software package for the analysis of electrochemical data.",
    entry_points={
        'console_scripts': [
            'madap_cli=madap_cli:main',
            'madap_gui=madap_gui:main',
        ],
    },
    extras_require={
        "dev": ["pytest>=3", ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='madap',
    name='MADAP',
    packages=find_packages(),
    py_modules=['madap_cli', 'madap_gui'],
    package_data={'madap/plotting/styles': ['*.mplstyle']},
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/fuzhanrahmanian/MADAP',
    version='1.2.7',
    zip_safe=False,
)

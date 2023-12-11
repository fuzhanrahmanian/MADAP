#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst', encoding="utf-8") as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst', encoding="utf-8") as history_file:
    history = history_file.read()

requirements = ["attrs==21.4.0",
        "matplotlib==3.5.3",
        "numpy==1.22.4",
        "pandas==1.4.2",
        "PySimpleGUI==4.60.3",
        "pytest==7.1.2",
        "scikit_learn==1.1.2",
        "impedance==1.4.1"]

test_requirements = ['pytest>=3', ]

setup(
    author="Fuzhan Rahmanian",
    author_email='fuzhanrahmanian@gmail.com',
    python_requires='>=3.9',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
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
    version='1.2.1',
    zip_safe=False,
)

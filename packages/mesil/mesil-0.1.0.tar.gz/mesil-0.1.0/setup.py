# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mesil', 'mesil.plot', 'mesil.process', 'mesil.tests.data']

package_data = \
{'': ['*']}

install_requires = \
['charset-normalizer>=3.1.0,<4.0.0',
 'matplotlib>=3.6.2,<4.0.0',
 'numpy>=1.23.4,<2.0.0',
 'openpyxl>=3.0.10,<4.0.0',
 'pandas>=1.5.1,<2.0.0',
 'typer[all]>=0.9.0,<0.10.0',
 'xlrd>=2.0.1,<3.0.0']

entry_points = \
{'console_scripts': ['mesil = mesil.cli:app']}

setup_kwargs = {
    'name': 'mesil',
    'version': '0.1.0',
    'description': 'Process and plot scientific data from various analyses (equipment specific)',
    'long_description': 'Mesil\n==============================\n\nSource code used in my undergraduate research "Investigation of cellular internalization and nanovalve endocytosis mechanisms in fluorescence-labeled rod morphology: a treatment for esophageal cancer".\n\n![Ilustration of the drug-loaded nanovalve system attacking a cancerous cell](img/graphical_abstract_dasilva2022.jpeg)\n',
    'author': 'Daniel Levita',
    'author_email': '71600818+danplevs@users.noreply.github.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.11,<4.0',
}


setup(**setup_kwargs)

# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mmca_mgqa']

package_data = \
{'': ['*']}

install_requires = \
['mgqa', 'torch']

setup_kwargs = {
    'name': 'mmca-mgqa',
    'version': '0.0.1',
    'description': 'mmca-mgqa - Pytorch',
    'long_description': '[![Multi-Modality](agorabanner.png)](https://discord.gg/qUtxnK2NMf)\n\n# MMCA-MGQA\nExperiments around using Multi-Modal Casual Attention with Multi-Grouped Query Attention\n\n\n# Appreciation\n* Lucidrains\n* Agorians\n\n\n# Install\n`pip install mmca-mgqa`\n\n# Usage\n\n# Architecture\n\n# Todo\n\n\n# License\nMIT\n',
    'author': 'Kye Gomez',
    'author_email': 'kye@apac.ai',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/kyegomez/mmca-mgqa',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)

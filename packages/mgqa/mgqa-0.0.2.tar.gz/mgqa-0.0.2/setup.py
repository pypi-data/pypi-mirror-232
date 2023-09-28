# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mgqa']

package_data = \
{'': ['*']}

install_requires = \
['torch']

setup_kwargs = {
    'name': 'mgqa',
    'version': '0.0.2',
    'description': 'mgqa - Pytorch',
    'long_description': '[![Multi-Modality](agorabanner.png)](https://discord.gg/qUtxnK2NMf)\n\n# MGQA\nThe open source implementation of the multi grouped query attention by the paper "GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints"\n\n\n[Paper Link](https://arxiv.org/abs/2305.13245)\n\n# Appreciation\n* Lucidrains\n* Agorians\n\n# Install\n``\n\n# Usage\n\n# Architecture\n\n# Todo\n\n\n# License\nMIT\n\n# Citations\n\n',
    'author': 'Kye Gomez',
    'author_email': 'kye@apac.ai',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/kyegomez/mgqa',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)

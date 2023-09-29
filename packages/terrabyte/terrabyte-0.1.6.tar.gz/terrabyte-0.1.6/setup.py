# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['terra_byte', 'terra_byte.model', 'terra_byte.training', 'terra_byte.utils']

package_data = \
{'': ['*']}

install_requires = \
['beartype>=0.8.1,<0.9.0',
 'einops>=0.3.0,<0.4.0',
 'torch>=1.9.0,<2.0.0',
 'triton>=1.0.0,<2.0.0']

setup_kwargs = {
    'name': 'terrabyte',
    'version': '0.1.6',
    'description': 'TerraByte - Pytorch',
    'long_description': 'None',
    'author': 'Kye Gomez',
    'author_email': 'kye@apac.ai',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)

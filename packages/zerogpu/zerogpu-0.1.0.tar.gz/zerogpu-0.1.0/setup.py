# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['zerogpu']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'zerogpu',
    'version': '0.1.0',
    'description': 'Helpers for Hugging Face ZeroGPU Spaces',
    'long_description': '## Hugging Face ZeroGPU Spaces\n',
    'author': 'cbensimon',
    'author_email': 'charles@huggingface.co',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)

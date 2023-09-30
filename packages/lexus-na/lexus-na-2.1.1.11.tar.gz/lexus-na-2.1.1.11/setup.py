# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['toyota_na',
 'toyota_na.vehicle',
 'toyota_na.vehicle.entity_types',
 'toyota_na.vehicle.vehicle_generations']

package_data = \
{'': ['*']}

install_requires = \
['PyJWT>=2.1.0', 'aiohttp>=3.8.1', 'cryptography>=35.0.0', 'pytz>=2022.1']

setup_kwargs = {
    'name': 'lexus-na',
    'version': '2.1.1.11',
    'description': 'Python client for Lexus North America service API',
    'long_description': 'Python client for Lexus North America service API',
    'author': 'Gavin Ni',
    'author_email': 'gisngy@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)

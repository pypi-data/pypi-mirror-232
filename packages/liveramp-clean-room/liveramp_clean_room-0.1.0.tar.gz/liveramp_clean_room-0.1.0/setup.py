# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['liveramp_clean_room', 'liveramp_clean_room.datahub']

package_data = \
{'': ['*'], 'liveramp_clean_room': ['config/*']}

install_requires = \
['Jinja2>=3.1.2,<4.0.0',
 'backoff>=2.2.1,<3.0.0',
 'cachetools>=4.2.1,<5.0.0',
 'numpy>=1.22.0,<2.0.0',
 'pandas>=1.5.3,<2.0.0',
 'pyarrow>=11.0.0,<12.0.0',
 'requests>=2.31.0,<3.0.0',
 'sqlglot>=18.1.0,<19.0.0',
 'toml>=0.10.2,<0.11.0']

setup_kwargs = {
    'name': 'liveramp-clean-room',
    'version': '0.1.0',
    'description': '',
    'long_description': '',
    'author': 'Datahub Eng',
    'author_email': 'datahub_ops@liveramp.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)

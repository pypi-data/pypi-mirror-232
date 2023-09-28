# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cybsi',
 'cybsi.cloud',
 'cybsi.cloud.auth',
 'cybsi.cloud.internal',
 'cybsi.cloud.iocean']

package_data = \
{'': ['*']}

install_requires = \
['enum-tools==0.9.0.post1', 'httpx>=0.23.1,<0.24.0']

extras_require = \
{':python_version < "3.8"': ['typing-extensions>=4.1.1,<5.0.0']}

setup_kwargs = {
    'name': 'cybsi-cloud-sdk',
    'version': '1.0.3',
    'description': 'Cybsi Cloud development kit',
    'long_description': None,
    'author': 'Cybsi Cloud developers',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)

# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['slack_cli_dashboard', 'slack_cli_dashboard.asynchronous']

package_data = \
{'': ['*']}

install_requires = \
['colorful>=0.5.4,<0.6.0', 'fabulous>=0.3.0,<0.4.0', 'slack_sdk>=3.0.0,<4.0.0']

entry_points = \
{'console_scripts': ['dashboard = slack_cli_dashboard.main:main']}

setup_kwargs = {
    'name': 'slack-cli-dashboard',
    'version': '0.1.2',
    'description': '',
    'long_description': 'None',
    'author': 'Jeff McGehee',
    'author_email': 'jlmcgehee21@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)

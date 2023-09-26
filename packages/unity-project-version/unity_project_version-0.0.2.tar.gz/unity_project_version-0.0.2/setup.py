# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['bootloader',
 'bootloader.unity',
 'bootloader.unity.cli',
 'bootloader.unity.model',
 'bootloader.unity.utils']

package_data = \
{'': ['*']}

install_requires = \
['perseus-core-library>=1.18.0,<2.0.0']

entry_points = \
{'console_scripts': ['unityprjver = bootloader.unity.cli.unityprjver:run']}

setup_kwargs = {
    'name': 'unity-project-version',
    'version': '0.0.2',
    'description': 'Unreal Engine project version utility',
    'long_description': '# Unity Project Version Management Command-line Interface (CLI)\nCommand-line interface utility for manipulating the project version of a Unity project.\n\n```shell\nunityprjver --path .\n```\n',
    'author': 'Daniel CAUNE',
    'author_email': 'daniel@bootloader.studio',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/Bootloader-Studio/unity-project-version',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)

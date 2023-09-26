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
    'version': '0.0.3',
    'description': 'Unreal Engine project version utility',
    'long_description': '# Unity Project Version Management Command-line Interface (CLI)\nCommand-line interface utility for manipulating the project version of a Unity project.\n\n```text\n% unityprjver --help\n\nusage: unityprjver [-h] [--build-number NUMBER] [--logging-level LEVEL] --path PATH [--replace-patch-version]\n                   [--update-version]\n\nUnreal Engine project version utility\n\noptions:\n  -h, --help            show this help message and exit\n  --build-number NUMBER\n                        specify the build number of the Unreal Engine project\n  --logging-level LEVEL\n                        specify the logging level (critical, error, warning, info, debug)\n  --path PATH           specify the path to the Unreal Engine project\n  --replace-patch-version\n                        indicate whether to replace the patch version of the Unreal Engine project with the specified\n                        build number. This argument MUST be used with the argument `--build-number`.\n  --update-version      indicate whether to update the defined in the Unreal Engine project. This argument MUST be\n                        used with the argument `--build-number`.\n```\n',
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

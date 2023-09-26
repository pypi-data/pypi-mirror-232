# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['flameshow', 'flameshow.pprof_parser', 'flameshow.render']

package_data = \
{'': ['*']}

install_requires = \
['cffi>=1.15.1,<2.0.0',
 'click>=8.1.7,<9.0.0',
 'textual>=0.37.1,<0.38.0',
 'typing-extensions>=4.7.1,<5.0.0']

entry_points = \
{'console_scripts': ['flameshow = flameshow.main:main']}

setup_kwargs = {
    'name': 'flameshow',
    'version': '0.1.4',
    'description': '',
    'long_description': '# Flameshow\n\n<a href="https://badge.fury.io/py/flameshow"><img src="https://badge.fury.io/py/flameshow.svg" alt="PyPI version"></a>\n\nFlameshow is a terminal Flamegraph viewer.\n\n![](./docs/flameshow.gif)\n\n## Features\n\n- Renders Flamegraphs in your terminal\n- Supports zooming in and displaying percentages\n- Keyboard input is prioritized\n- However, all operations in Flameshow can also be performed using the mouse\n- Can switch to different sample types\n\n## Install\n\n```shell\npip install flameshow\n```\n\n## Usage\n\nView golang\'s goroutine dump:\n\n```shell\n$ curl http://localhost:9100/debug/pprof/goroutine -o goroutine.out\n$ flameshow goroutine.out\n```\n\nOnce you open flameshow, you should be able to use it, the UI is very easy to\nuse.\n',
    'author': 'laixintao',
    'author_email': 'laixintaoo@gmail.com',
    'maintainer': 'laixintao',
    'maintainer_email': 'laixintaoo@gmail.com',
    'url': 'https://github.com/laixintao/flameshow',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)

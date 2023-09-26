# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['easyeda', 'easyeda.core']

package_data = \
{'': ['*']}

install_requires = \
['svg-path>=6.3,<7.0']

setup_kwargs = {
    'name': 'easyeda-python-sdk',
    'version': '0.1.0a1',
    'description': 'Python tools & design framework for EasyEDA ',
    'long_description': '# easyeda-python-sdk\nPython tools &amp; design framework for EasyEDA\n\n## Install \n\n```shell\npip install easyeda-python-sdk\n```\n\n## Example\n\n```python\nfrom easyeda import PCB, Point\n\npcb = PCB()\npcb.BOARD_OUTLINE_LAYER.add_rectangle(width=1000, height=500, corner_radius=50)\n\npcb.DOCUMENT_LAYER.add_text("Hello from easyeda-python-sdk",\n                            font_size=40, font_width=4, position=Point(-500, 300))\n\nfor p in [Point(-430, 180), Point(430, 180), Point(-430, -180), Point(430, -180)]:\n    pcb.add_hole(80, center=p)\n\nprint(pcb)\n```\n\n![docs/images/hello-world.png](docs/images/hello-world.png)\n\n',
    'author': 'Thomas Mahé',
    'author_email': 'contact@tmahe.dev',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)

# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['autonode_diagrams']

package_data = \
{'': ['*']}

install_requires = \
['diagrams>=0.6.0', 'pillow>=9.2.0']

setup_kwargs = {
    'name': 'autonode-diagrams',
    'version': '1.0.2',
    'description': 'Automatically generate node icons for Python Diagrams based on label text',
    'long_description': '# Autonode Diagrams\n\nThe Python [Diagrams](https://diagrams.mingrammer.com) project is an excellent resource for drawing technical diagrams using code, allowing diagrams to be version controlled easily and you to spend time writing content rather than fussing over formatting.\n\nHowever, one current limitation is that all nodes of the diagram must have both a label and an icon to be displayed. Although [Diagrams](https://diagrams.mingrammer.com) comes with a large number of relevant node types and corresponding icons pre-installed, and the [custom node](https://diagrams.mingrammer.com/docs/nodes/custom) allows you to extend this even further, sometimes you don\'t have a suitable icon for the node available, or you want to quickly generate a diagram and worry about populating the icons later.\n\nThis package extends the [Diagram\'s Custom Node](https://diagrams.mingrammer.com/docs/nodes/custom) and automatically generates an icon based on the text in the node\'s label if no icon is provided. It is designed to be used in conjunction with, not as a replacement to, [Diagrams](https://diagrams.mingrammer.com).\n\n![Demonstration](https://raw.githubusercontent.com/Machione/autonode-diagrams/main/demonstration.png)\n\n## Quick Start\n\nMost of this code is taken from the [Diagram\'s Quick Start guide](https://diagrams.mingrammer.com/docs/getting-started/installation#quick-start) plus [Custom nodes with remote icons guide](https://diagrams.mingrammer.com/docs/nodes/custom#custom-with-remote-icons). This is to show how Autonode Diagram\'s `Icon` class integrates seamlessly with the rest of the regular Python Diagram\'s functionality, allowing the two to be used side-by-side.\n\n```python\nfrom diagrams import Diagram\nfrom diagrams.programming.language import Python\nfrom diagrams.custom import Custom\nfrom autonode_diagrams import Icon\nfrom urllib.request import urlretrieve\n\nwith Diagram("Quick Start", show=False):\n    # Get a remote PNG to prove that autonode_diagrams.Icon can also work just like normal diagrams.custom.Custom\n    emoji_url = "https://openmoji.org/php/download_asset.php?type=emoji&emoji_hexcode=2728&emoji_variant=color"\n    emoji_fp = "./sparkle.png"\n    urlretrieve(emoji_url, emoji_fp) # You can delete this file later\n    \n    Icon("Just a label, no icon given", border=True) >> Python("Autonode Diagrams") >> Icon("Something beautiful", emoji_fp)\n```\n\n## Prerequisites\n\n- Arial font.\n- Python [Diagrams](https://diagrams.mingrammer.com/docs/getting-started/installation) along with their dependencies (specifically [Graphviz](https://graphviz.gitlab.io/download/) will need to be installed).\n',
    'author': 'Ryan McKeown',
    'author_email': 'ryanmckeown@mail4me.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)

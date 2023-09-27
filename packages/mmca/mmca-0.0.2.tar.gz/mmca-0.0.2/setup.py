# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mmca']

package_data = \
{'': ['*']}

install_requires = \
['torch']

setup_kwargs = {
    'name': 'mmca',
    'version': '0.0.2',
    'description': 'MMCA - Pytorch',
    'long_description': '[![Multi-Modality](agorabanner.png)](https://discord.gg/qUtxnK2NMf)\n\n# Multi-Modal Causal Attention\nThe open source community\'s implementation of the all-new Multi-Modal Causal Attention from "DeepSpeed-VisualChat: Multi-Round Multi-Image Interleave Chat via Multi-Modal Causal Attention"\n\n\n[Paper Link](https://arxiv.org/pdf/2309.14327.pdf)\n\n# Appreciation\n* Lucidrains\n* Agorians\n\n\n\n# Install\n`pip install mmca`\n\n# Usage\n```python\nimport torch \nfrom mmca.main import MultiModalCausalAttention\n\n\nattn = MultiModalCausalAttention(dim=512, heads=8)\n\nx = torch.randn(1, 10, 512)\ny = torch.randn(1, 20, 512)\n\n#create a mask for the text\n# mask = torch.ones(1, 20).bool()\n\nx, y = attn(x, y)\n\nprint(x)\n# print(y)\n```\n\n# Architecture\n\n# Todo\n\n\n# License\nMIT\n\n# Citations\n\n',
    'author': 'Kye Gomez',
    'author_email': 'kye@apac.ai',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/kyegomez/MMCA',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)

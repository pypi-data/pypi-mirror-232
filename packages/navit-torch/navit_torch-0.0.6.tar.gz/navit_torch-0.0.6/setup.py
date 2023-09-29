# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['navit']

package_data = \
{'': ['*']}

install_requires = \
['einops', 'torch', 'zetascale']

setup_kwargs = {
    'name': 'navit-torch',
    'version': '0.0.6',
    'description': 'navit - Pytorch',
    'long_description': '[![Multi-Modality](agorabanner.png)](https://discord.gg/qUtxnK2NMf)\n\n# NaViT\nMy implementation of "Patch n’ Pack: NaViT, a Vision Transformer for any Aspect Ratio and Resolution"\n\n[Paper Link](https://arxiv.org/pdf/2307.06304.pdf)\n\n# Appreciation\n* Lucidrains\n* Agorians\n\n# Install\n`pip install navit-torch`\n\n# Usage\n```pytorch\nimport torch\nfrom navit.main import NaViT\n\n\nn = NaViT(\n    image_size = 256,\n    patch_size = 32,\n    num_classes = 1000,\n    dim = 1024,\n    heads = 16,\n    mlp_dim=2048,\n    dropout=0.1,\n    emb_dropout=0.1,\n    token_dropout_prob=0.1\n)\n\nimages = [\n    [torch.randn(3, 256, 256), torch.randn(3, 128, 128)],\n    [torch.randn(3, 256, 256), torch.randn(3, 256, 128)],\n    [torch.randn(3, 64, 256)]\n]\n\npreds = n(images)\n```\n\n# Architecture\n\n# Todo\n\n\n# License\nMIT\n\n# Citations\n```\n@misc{2307.06304,\nAuthor = {Mostafa Dehghani and Basil Mustafa and Josip Djolonga and Jonathan Heek and Matthias Minderer and Mathilde Caron and Andreas Steiner and Joan Puigcerver and Robert Geirhos and Ibrahim Alabdulmohsin and Avital Oliver and Piotr Padlewski and Alexey Gritsenko and Mario Lučić and Neil Houlsby},\nTitle = {Patch n\' Pack: NaViT, a Vision Transformer for any Aspect Ratio and Resolution},\nYear = {2023},\nEprint = {arXiv:2307.06304},\n}\n```\n',
    'author': 'Kye Gomez',
    'author_email': 'kye@apac.ai',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/kyegomez/navit',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)

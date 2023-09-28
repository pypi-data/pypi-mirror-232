# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mmca_mgqa']

package_data = \
{'': ['*']}

install_requires = \
['mgqa', 'torch']

setup_kwargs = {
    'name': 'mmmgqa',
    'version': '0.0.2',
    'description': 'mmca-mgqa - Pytorch',
    'long_description': '[![Multi-Modality](agorabanner.png)](https://discord.gg/qUtxnK2NMf)\n\n# Multi-Modal Casual Multi-Grouped Query Attention\nExperiments around using Multi-Modal Casual Attention with Multi-Grouped Query Attention\n\n\n# Appreciation\n* Lucidrains\n* Agorians\n\n\n# Install\n`pip install mmmgqa`\n\n# Usage\n```python\nimport torch \nfrom mmca_mgqa.attention import SimpleMMCA\n\n# Define the dimensions\ndim = 512\nhead = 8\nseq_len = 10\nbatch_size = 32\n\n#attn\nattn = SimpleMMCA(dim=dim, heads=head)\n\n#random tokens\nv = torch.randn(batch_size, seq_len, dim)\nt = torch.randn(batch_size, seq_len, dim)\n\n#pass the tokens throught attn\ntokens = attn(v, t)\n\nprint(tokens)\n```\n\n# Architecture\n\n# Todo\n\n\n# License\nMIT\n',
    'author': 'Kye Gomez',
    'author_email': 'kye@apac.ai',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/kyegomez/mmca-mgqa',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)

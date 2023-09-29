# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['local_sfmx']

package_data = \
{'': ['*']}

install_requires = \
['torch']

setup_kwargs = {
    'name': 'local-sfmx',
    'version': '0.0.4',
    'description': 'local-sftmx - Pytorch',
    'long_description': '[![Multi-Modality](agorabanner.png)](https://discord.gg/qUtxnK2NMf)\n\n# LocalSoftmax\nLocal Softmax parallelize the softmax computation by splitting the tensor into smaller sub-tensors and applying the softmax function on each of these smaller tensors independently. In other words, we want to compute a "local" softmax on each chunk of the tensor, instead of on the entire tensor.\n\n# Appreciation\n* Lucidrains\n* Agorians\n\n\n\n# Install\n`pip install local-sftmx`\n\n\n## Usage\n```python\nimport torch\nfrom local_sfmx import local_softmax\n\ntensor = torch.rand(10, 5)\nresult = local_softmax(tensor, 2)\nprint(result)\n```\n\n# Algorithm\nfunction LocalSoftmax(tensor, num_chunks):\n    split tensors into `num_chunks` smaller tensors\n    for each smaller tensor:\n        apply standard softmax\n    concatenate the results\n    return concatenated tensor\n\n# License\nMIT\n\n',
    'author': 'Kye Gomez',
    'author_email': 'kye@apac.ai',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/kyegomez/LocalSoftmax',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)

# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['glovpy']

package_data = \
{'': ['*']}

install_requires = \
['gensim>=4.3.0,<5.0.0']

setup_kwargs = {
    'name': 'glovpy',
    'version': '0.1.0',
    'description': 'Interface for using the canonical C GloVe embedding implementation in Python',
    'long_description': '# glovpy\nPackage for interfacing Stanford\'s C GloVe implementation from Python.\n\n## Installation\n\nInstall glovpy from PyPI:\n\n```bash\npip install glovpy\n```\n\nAdditionally the first time you import glopy it will build GloVe from scratch on your system.\n\n## Requirements\nWe highly recommend that you use a Unix-based system, preferably a variant of Debian.\nThe package needs `git`, `make` and a C compiler (`clang` or `gcc`) installed.\n\n## Example Usage\nHere\'s a quick example of how to train GloVe on 20newsgroups using Gensim\'s tokenizer.\n\n```python\nfrom gensim.utils import tokenize\nfrom sklearn.datasets import fetch_20newsgroups\n\nfrom glovpy import GloVe\n\ntexts = fetch_20newsgroups().data\ncorpus = [list(tokenize(text, lowercase=True, deacc=True)) for text in texts]\n\nmodel = GloVe(vector_size=25)\nmodel.train(corpus)\n\nfor word, similarity in model.wv.most_similar("god"):\n    print(f"{word}, sim: {similarity}")\n```\n\n|   word     |   similarity   |\n|------------|---------------|\n| existence  |  0.9156746864 |\n| jesus      |  0.8746870756 |\n| lord       |  0.8555182219 |\n| christ     |  0.8517201543 |\n| bless      |  0.8298447728 |\n| faith      |  0.8237065077 |\n| saying     |  0.8204566240 |\n| therefore  |  0.8177698255 |\n| desires    |  0.8094088435 |\n| telling    |  0.8083973527 |\n',
    'author': 'Márton Kardos',
    'author_email': 'power.up1163@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)

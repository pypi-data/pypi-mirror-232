# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['schnitsum', 'schnitsum.bin']

package_data = \
{'': ['*']}

install_requires = \
['fire>=0.4.0,<0.5.0',
 'sienna>=0.2.0',
 'torch>=2.0.0',
 'transformers>=4.33.2,<5.0.0']

entry_points = \
{'console_scripts': ['schnitsum = schnitsum.bin.summarize:cli']}

setup_kwargs = {
    'name': 'schnitsum',
    'version': '0.4.10',
    'description': '',
    'long_description': '# Schnitsum: Easy to use neural network based summarization models\n\nThis package enables to generate summaries of you documents of interests.\n\nCurrently, we support following models,\n\n- [BART (large)](https://aclanthology.org/2020.acl-main.703) fine-tuned on computer science papers (ref. [SciTLDR](https://aclanthology.org/2020.findings-emnlp.428)).\n  - Model name: `sobamchan/bart-large-scitldr`\n- [BART (large)](https://aclanthology.org/2020.acl-main.703) fine-tuned on computer science papers (ref. [SciTLDR](https://aclanthology.org/2020.findings-emnlp.428)). Then distilled (by [`shrink and fine-tune`](http://arxiv.org/abs/2010.13002)) to have 65% parameters less.\n  - Model name: `sobamchan/bart-large-scitldr-distilled-3-3`\n- [BART (large)](https://aclanthology.org/2020.acl-main.703) fine-tuned on computer science papers (ref. [SciTLDR](https://aclanthology.org/2020.findings-emnlp.428)). Then distilled (by [`shrink and fine-tune`](http://arxiv.org/abs/2010.13002)) to have 37% parameters less.\n  - Model name: `sobamchan/bart-large-scitldr-distilled-12-3`\n- [mBART (large, en-to-de)](https://aclanthology.org/2020.acl-main.703) fine-tuned on computer science papers, English papers and German summaries (ref. [X-SciTLDR](https://dl.acm.org/doi/abs/10.1145/3529372.3530938)).\n  - Model name: `sobamchan/mbart-large-xscitldr-de`\n- [BART (large)](https://aclanthology.org/2020.acl-main.703) fine-tuned on XSum, BCC news article lead sentences in English. (ref. [X-SciTLDR](https://dl.acm.org/doi/abs/10.1145/3529372.3530938)).\n  - Model name: `facebook/bart-large-xsum`\n\nwe are planning to expand coverage soon to other sizes, domains, languages, models soon.\n\n\n# Installation\n\n```bash\npip install schnitsum  # or poetry add schnitsum\n```\n\nThis will let you generate summaries with CPUs only, if you want to utilize your GPUs, please follow the instruction by PyTorch, [here](https://pytorch.org/get-started/locally/).\n\n\n# Usage\n\n## From Command Line\nPass document as an argument and print the summary\n```sh\n> schnitsum --model-name sobamchan/bart-large-scitldr-distilled-3-3 --text "Text to summarize"\n```\n\nPass documents as a file and save summaries in a file.\nInput file needs to contain documents line by line. [example](https://github.com/sobamchan/schnitsum/blob/main/examples/docs.txt)\n```sh\n> schnitsum --model-name sobamchan/bart-large-scitldr-distilled-3-3 --file docs.txt --opath sums.txt\n```\n\n## From Python\n```py3\nfrom schnitsum import SchnitSum\n\nmodel = SchnitSum("sobamchan/bart-large-scitldr-distilled-3-3")\ndocs = [\n    "Document you want to summarize."\n]\nsummaries = model(docs)\nprint(summaries)\n```\n',
    'author': 'sobamchan',
    'author_email': 'oh.sore.sore.soutarou@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)

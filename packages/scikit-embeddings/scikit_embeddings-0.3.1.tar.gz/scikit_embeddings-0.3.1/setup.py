# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['skembeddings', 'skembeddings.models', 'skembeddings.tokenizers']

package_data = \
{'': ['*']}

install_requires = \
['catalogue>=2.0.8,<3.0.0',
 'confection>=0.1.0,<0.2.0',
 'gensim>=4.3.0,<5.0.0',
 'huggingface-hub>=0.16.0,<0.17.0',
 'scikit-learn>=1.2.0,<2.0.0',
 'tokenizers>=0.13.0,<0.14.0']

extras_require = \
{'glove': ['glovpy>=0.1.0,<0.2.0']}

setup_kwargs = {
    'name': 'scikit-embeddings',
    'version': '0.3.1',
    'description': 'Tools for training word and document embeddings in scikit-learn.',
    'long_description': '<img align="left" width="82" height="82" src="assets/logo.svg">\n\n# scikit-embeddings\n\n<br>\nUtilites for training, storing and using word and document embeddings in scikit-learn pipelines.\n\n## Features\n - Train Word and Paragraph embeddings in scikit-learn compatible pipelines.\n - Fast and performant trainable tokenizer components from `tokenizers`.\n - Easy to integrate components and pipelines in your scikit-learn workflows and machine learning pipelines.\n - Easy serialization and integration with HugginFace Hub for quickly publishing your embedding pipelines.\n\n### What scikit-embeddings is not for:\n - Training transformer models and deep neural language models (if you want to do this, do it with [transformers](https://huggingface.co/docs/transformers/index))\n - Using pretrained sentence transformers (use [embetter](https://github.com/koaning/embetter))\n\n## Installation\n\nYou can easily install scikit-embeddings from PyPI:\n\n```bash\npip install scikit-embeddings\n```\n\nIf you want to use GloVe embedding models, install alogn with glovpy:\n\n```bash\npip install scikit-embeddings[glove]\n```\n\n## Example Pipelines\n\nYou can use scikit-embeddings with many many different pipeline architectures, I will list a few here:\n\n### Word Embeddings\n\nYou can train classic vanilla word embeddings by building a pipeline that contains a `WordLevel` tokenizer and an embedding model:\n\n```python\nfrom skembedding.tokenizers import WordLevelTokenizer\nfrom skembedding.models import Word2VecEmbedding\nfrom skembeddings.pipeline import EmbeddingPipeline\n\nembedding_pipe = EmbeddingPipeline(\n    WordLevelTokenizer(),\n    Word2VecEmbedding(n_components=100, algorithm="cbow")\n)\nembedding_pipe.fit(texts)\n```\n\n### Fasttext-like\n\nYou can train an embedding pipeline that uses subword information by using a tokenizer that does that.\nYou may want to use `Unigram`, `BPE` or `WordPiece` for these purposes.\nFasttext also uses skip-gram by default so let\'s change to that.\n\n```python\nfrom skembedding.tokenizers import UnigramTokenizer\nfrom skembedding.models import Word2VecEmbedding\nfrom skembeddings.pipeline import EmbeddingPipeline\n\nembedding_pipe = EmbeddingPipeline(\n    UnigramTokenizer(),\n    Word2VecEmbedding(n_components=250, algorithm="sg")\n)\nembedding_pipe.fit(texts)\n```\n\n### Paragraph Embeddings\n\nYou can train Doc2Vec paragpraph embeddings with the chosen choice of tokenization.\n\n```python\nfrom skembedding.tokenizers import WordPieceTokenizer\nfrom skembedding.models import ParagraphEmbedding\nfrom skembeddings.pipeline import EmbeddingPipeline, PretrainedPipeline\n\nembedding_pipe = EmbeddingPipeline(\n    WordPieceTokenizer(),\n    ParagraphEmbedding(n_components=250, algorithm="dm")\n)\nembedding_pipe.fit(texts)\n```\n\n## Serialization\n\nPipelines can be safely serialized to disk:\n\n```python\nembedding_pipe.to_disk("output_folder/")\n\npretrained = PretrainedPipeline("output_folder/")\n```\n\nOr published to HugginFace Hub:\n\n```python\nfrom huggingface_hub import login\n\nlogin()\nembedding_pipe.to_hub("username/name_of_pipeline")\n\npretrained = PretrainedPipeline("username/name_of_pipeline")\n```\n\n## Text Classification\n\nYou can include an embedding model in your classification pipelines by adding some classification head.\n\n```python\nfrom sklearn.linear_model import LogisticRegression\nfrom sklearn.model_selection import train_test_split\nfrom sklearn.metrics import classification_report\n\nX_train, X_test, y_train, y_test = train_test_split(X, y)\n\ncls_pipe = make_pipeline(pretrained, LogisticRegression())\ncls_pipe.fit(X_train, y_train)\n\ny_pred = cls_pipe.predict(X_test)\nprint(classification_report(y_test, y_pred))\n```\n\n',
    'author': 'Márton Kardos',
    'author_email': 'power.up1163@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)

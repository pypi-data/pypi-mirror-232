# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyreveal']

package_data = \
{'': ['*'],
 'pyreveal': ['revealjs/*',
              'revealjs/.github/*',
              'revealjs/.github/workflows/*',
              'revealjs/css/*',
              'revealjs/css/print/*',
              'revealjs/css/theme/*',
              'revealjs/css/theme/source/*',
              'revealjs/css/theme/template/*',
              'revealjs/dist/*',
              'revealjs/dist/theme/*',
              'revealjs/dist/theme/fonts/league-gothic/*',
              'revealjs/dist/theme/fonts/source-sans-pro/*',
              'revealjs/examples/*',
              'revealjs/examples/assets/*',
              'revealjs/js/*',
              'revealjs/js/components/*',
              'revealjs/js/controllers/*',
              'revealjs/js/utils/*',
              'revealjs/plugin/highlight/*',
              'revealjs/plugin/markdown/*',
              'revealjs/plugin/math/*',
              'revealjs/plugin/notes/*',
              'revealjs/plugin/search/*',
              'revealjs/plugin/zoom/*',
              'revealjs/test/*',
              'revealjs/test/assets/*']}

setup_kwargs = {
    'name': 'pyreveal',
    'version': '0.1.0',
    'description': 'A Python library to simplify the creation of presentations using Reveal.js.',
    'long_description': None,
    'author': 'Ali Tavallaie',
    'author_email': 'a.tavallaie@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)

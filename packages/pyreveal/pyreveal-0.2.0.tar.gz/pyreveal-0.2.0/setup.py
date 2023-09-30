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
    'version': '0.2.0',
    'description': 'A Python library to simplify the creation of presentations using Reveal.js.',
    'long_description': '================\nPyReveal Library\n================\n\nPyReveal is a Python library that allows users to generate Reveal.js presentations programmatically. With PyReveal, you can easily create slides, set themes, transitions, and even add custom backgrounds like images or videos.\n\nFeatures\n========\n\n- Create Reveal.js presentations using Python.\n- Support for slide themes and transitions.\n- Error handling and validation for slide content.\n- Export presentations to HTML.\n- Support for slide backgrounds, including images, videos, and colors.\n- Parallax background support.\n\nInstallation\n============\n\n.. code-block:: bash\n\n   pip install pyreveal\n\nUsage\n=====\n\n.. code-block:: python\n\n   from pyreveal import PyReveal, ImageBackground\n\n   presentation = PyReveal(title="My Presentation", theme="white", transition="slide")\n   presentation.add_slide("Welcome to PyReveal!")\n   bg_image = ImageBackground(image_url="path/to/image.jpg")\n   presentation.add_slide("This slide has a background image!", background=bg_image)\n   presentation.save_to_file("my_presentation.html")\n\nFor more advanced usage and features, please refer to the documentation.\n\nContribute\n==========\n\n- Issue Tracker: `https://github.com/tavallaie/pyreveal/issues`\n- Source Code: `https://github.com/tavallaie/pyreveal`\n\nSupport\n=======\n\nIf you are having issues, please let us know. You can report issues on the issue tracker mentioned above.\n\n\nLicense\n=======\n\nThe project is licensed under the MIT license. See the `LICENSE`_ file for more details.\n\n.. _LICENSE: ./LICENSE\n',
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

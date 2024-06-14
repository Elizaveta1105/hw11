import sys
import os

sys.path.append(os.path.abspath('../..'))

project = 'contacts'
copyright = '2024, Liza'
author = 'Liza'

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.napoleon']

templates_path = ['_templates']
exclude_patterns = []


html_theme = 'nature'
html_static_path = ['_static']

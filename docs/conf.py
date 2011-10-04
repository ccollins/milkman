# -*- coding: utf-8 -*-
import sys, os
sys.path.append("../")

extensions = []
templates_path = ['_templates']
source_suffix = '.txt'
master_doc = 'index'

project = 'milkman'
copyright = '2011'
version = '4.5'
release = '4.5'

today_fmt = '%B %d, %Y'
exclude_trees = []
pygments_style = 'sphinx'
html_style = 'default.css'
html_static_path = ['_static']
html_last_updated_fmt = '%b %d, %Y'

htmlhelp_basename = 'milkmandoc'
latex_documents = [
  ('index', 'milkman.tex', 'Milkman Documentation',
   '', 'manual'),
]

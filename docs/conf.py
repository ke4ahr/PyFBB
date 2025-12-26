
# Sphinx configuration for PyFBB documentation

project = 'PyFBB'
copyright = '2025, Kris Kirby, KE4AHR'
author = 'Kris Kirby, KE4AHR'
release = '0.1.2'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'myst_parser'
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'alabaster'
html_static_path = ['_static']

source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

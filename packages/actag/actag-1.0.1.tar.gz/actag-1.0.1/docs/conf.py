# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'AcTag: Opti-Acoustic Fiducial Markers for Underwater Localization and Mapping'
copyright = '2023, BYU-FRoStLab'
author = 'BYU-FRoStLab'
html_favicon = 'favicon.ico'

import sys
path_to_actag_py = __file__[:__file__.find("docs")] + "actag_detection/src/"
print(path_to_actag_py)
sys.path.append(path_to_actag_py)

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autosectionlabel', 'sphinx.ext.autodoc', "myst_parser"]

myst_enable_extensions = [
    "amsmath",
    "attrs_inline",
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Option to throw errors for smaller issues
# nitpicky = True

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# --- Currently unused configuration that allows us to add a custom logo to the top left of the docs ---
# html_logo = "../actag_families/image_files/example_images/AcTagLogo4.png"
# html_theme_options = {
#     'logo_only': True,
#     'display_version': False,
# }
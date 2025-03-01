"""
interpreter-smol - A powerful interpreter with evolving agents built on SmolaGents
"""

from .core.interpreter import Interpreter, main

__version__ = "0.2.0"  # Updated to match setup.py

# Make main function available for CLI
__main__ = main  # setup.py uses this for console_scripts

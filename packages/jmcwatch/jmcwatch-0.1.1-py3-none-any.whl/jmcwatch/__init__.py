# jmcwatch/__init__.py

# Define a package-level variable
PACKAGE_VERSION = '0.1.0'

# Import the main function from your CLI module
from .cli import main

# Initialize package-level configuration
CONFIG = {
    'debug': False,
}

# Optionally, define what should be available when someone uses "from package import *"
__all__ = ['main', 'PACKAGE_VERSION']

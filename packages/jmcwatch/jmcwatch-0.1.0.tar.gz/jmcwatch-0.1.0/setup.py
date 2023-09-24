from setuptools import setup, find_packages

setup(
    name='jmcwatch',
    version='0.1.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'jmcwatch=jmcwatch.cli:main',
        ],
    },
    install_requires=[
        'click',
        'watchdog'
    ],
    author='amandin',
    author_email='amawwdin@gmail.com',
    description='Compile JMC code on save',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license='MIT',
)

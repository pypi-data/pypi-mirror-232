from setuptools import setup, find_packages

setup(
    name='globestylizer',
    version='0.1.7',
    packages=find_packages(where='src/state_style'),  
    install_requires=[
        'pandas',
    ],
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)

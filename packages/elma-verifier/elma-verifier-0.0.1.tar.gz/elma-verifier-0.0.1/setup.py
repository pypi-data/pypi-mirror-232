from setuptools import setup, find_packages

setup(
    name='elma-verifier',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'selenium'
    ],
    author='Mathias Mjømen',
    description='A module for checking an organization number against the ELMA-registry.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
)
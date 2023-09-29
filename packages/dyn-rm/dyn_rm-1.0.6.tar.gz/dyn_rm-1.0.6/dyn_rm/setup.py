from setuptools import setup, find_packages

setup(
    name='dyn_rm',
    version='1.0.0',
    description='A Dynamic Resource Manager for Dyn_PRRTE, Dyn_PMIx and Dyn_OMPI',
    author='Dominik Huber',
    author_email='your@email.com',
    packages=find_packages(),
    install_requires=[
        # List any dependencies your package requires
        'pypmix', 
        'asyncio'
    ],
)

from setuptools import setup, find_packages


setup(
    name='dyn_rm',
    version='1.0.6',
    description='A Dynamic Resource Manager for Dyn_PRRTE, Dyn_PMIx and Dyn_OMPI',
    author='Dominik Huber',
    author_email='domi.huber@tum.de',
    url='https://gitlab.inria.fr/dynres/dyn-procs/dyn_rm',
    packages=find_packages(),
    install_requires=[
        # List any dependencies your package requires
        'pypmix', 
    ],
    entry_points={
    	'console_scripts': [
    		'dyn_rm = dyn_rm.dynamic_resource_manager:main',
    	],
    },
)

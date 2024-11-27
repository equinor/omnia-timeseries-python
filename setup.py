from setuptools import setup, find_packages

setup(
    name='omnia_timeseries',
    version='1.3.10',
    description='A package for Omnia timeseries functionality',
    author='Your Name',
    author_email='your_email@example.com',
    packages=find_packages(where='src'),  # Look for packages in the `src` directory
    package_dir={'': 'src'},    
    install_requires=[
        'azure-identity',
        'requests',                 
        'azure-storage-blob'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)

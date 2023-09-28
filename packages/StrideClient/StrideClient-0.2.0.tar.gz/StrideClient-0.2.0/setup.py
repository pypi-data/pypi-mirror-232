from setuptools import setup, find_packages

setup(
    name='StrideClient',  # Change this to your library name
    version='0.2.0',
    description='Library for interfacing with STRIDE devices',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Brian Benchoff',
    author_email='brian.benchoff@span.io',
    url='https://github.com/spanio/STRIDE-driver',
    packages=find_packages(),
    install_requires=[
        'pyModbusTCP>=0.1.8',  # Specify the minimum version you need
        'pymodbus>=2.5.3',  # Specify the minimum version you need
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',  # Change if you have a different license
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)


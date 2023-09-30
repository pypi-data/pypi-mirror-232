from setuptools import setup, find_packages

setup(
    name='globestylizer',
    version='0.1.1',
    packages=find_packages(where='src'),  
    package_dir={'': 'src'}, 
    install_requires=[
        'pandas',
    ],
    # Add the long_description and long_description_content_type fields here:
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)

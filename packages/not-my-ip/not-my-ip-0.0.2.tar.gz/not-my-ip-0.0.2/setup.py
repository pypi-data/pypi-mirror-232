from setuptools import setup

with open('README.md', 'r') as f:
    long_description = f.read()

with open('requirements.txt', 'r') as f:
    requirements = f.read().splitlines()

setup(
    name='not-my-ip',
    version='0.0.2',
    install_requires=requirements,
    author='Samuel Gunter',
    author_email='sgunter@utexas.edu',
    description='A CLI tool to generate a random IP address that is not your own',
    long_description=long_description,
    long_description_content_type='text/markdown',
    entry_points={
        'console_scripts': [
            'not-my-ip = main:cli'
        ]
    }
)

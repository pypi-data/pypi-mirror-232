from setuptools import setup

with open('README.md', 'r') as f:
    long_description = f.read()

with open('requirements.txt', 'r') as f:
    requirements = f.read().splitlines()

setup(
    name='not-my-ip',
    version='0.0.1',
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'not-my-ip = main:cli'
        ]
    }
)

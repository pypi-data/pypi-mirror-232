from pathlib import Path
from setuptools import setup, find_packages

with open('README.md') as f:
  readme = f.read()

with open('LICENSE') as f:
  license = f.read()

setup(
    name='basenji',
    version='0.1',
    description='Sequential regulatory activity machine learning',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='David Kelley',
    author_email='drk@calicolabs.com',
    url='https://github.com/calico/basenji',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=[
        l.strip() for l in
        Path('requirements.txt').read_text('utf-8').splitlines()
    ]
)
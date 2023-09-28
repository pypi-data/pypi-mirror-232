#!/usr/bin/env python3

from setuptools import setup
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

pkg = 'hardcoded'

setup(name = pkg,
      version = '0.13.22',
      description = 'For everything that you really should not be hardcoding.',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url = f'https://pypi.org/project/{pkg}/',
      author = 'moizuo',
      author_email = f'no_spam@example.com',
      classifiers = [
          'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
          ],
      packages = [pkg],
      install_requires = [
          'Click>=8.0.1',
          'pyyaml',
          'python-gnupg',
      ],
      extras_require = {
          'encryption_without_pgp': [
              'cryptography>=39.0.0',
              'cffi>=1.15.1',
          ],
      },
      entry_points = {
          'console_scripts': [
              'hardcoded = hardcoded:cli'
              ]
          },
      zip_safe = False)


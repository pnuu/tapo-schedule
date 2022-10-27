"""Package setup."""

from setuptools import find_packages, setup

with open('README.md') as readme_file:
    README = readme_file.read()

setup_args = dict(
    name='tapo-schedule',
    version='0.0.1',
    description='A module for scheduling and controlling TP-link Tapo plugs and bulbs.',
    long_description_content_type="text/markdown",
    long_description=README,
    license='MIT',
    packages=find_packages(),
    author='Panu Lahtinen',
    author_email='pnuu+git@iki.fi',
    keywords=['Tapo', 'TP-Link', 'scheduling'],
    url='https://github.com/pnuu/tapo-schedule',
    scripts=['bin/run_schedule.py', ]
    # download_url='https://pypi.org/project/tapo-schedule/'
)

install_requires = [
    'pycryptodome>=3.9.8',
    'pkcs7>=0.1.2',
    'requests>=2.24.0',
]

if __name__ == '__main__':
    setup(**setup_args, install_requires=install_requires)

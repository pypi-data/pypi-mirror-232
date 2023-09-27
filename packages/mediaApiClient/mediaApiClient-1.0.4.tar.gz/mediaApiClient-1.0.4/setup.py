from setuptools import setup, find_packages

version = '1.0.4'

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='mediaApiClient',
    version=version,
    packages=find_packages(),
    install_requires=[
        'pydantic~=2.2.1',
        'setuptools~=65.5.1',
        'requests~=2.31.0',
    ],
    author='Semyon Shilovskiy',
    author_email='semen.shilovski@yandex.ru',
    description='A library for working with REST API of CAG',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='Apache License, Version 2.0, see LICENSE file',
    url='https://github.com/semen-shilovski/mediaApiClient',
)

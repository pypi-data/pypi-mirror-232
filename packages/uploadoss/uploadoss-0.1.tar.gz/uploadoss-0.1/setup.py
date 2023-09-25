from setuptools import setup, find_packages

setup(
    name='uploadoss',
    version='0.1',
    author='Binghe',
    packages=find_packages(),
    install_requires=[
        'oss2',
        'pandas',
        'pymysql',
        'configparser'
    ],
)

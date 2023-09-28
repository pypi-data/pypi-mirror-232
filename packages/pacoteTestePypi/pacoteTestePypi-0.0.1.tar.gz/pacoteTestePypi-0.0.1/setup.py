from setuptools import setup

with open("README.md", "r") as fh:
    readme = fh.read()

setup(name='pacoteTestePypi',
    version='0.0.1',
    #url='https://github.com/renanrmoreira',
    license='MIT License',
    author='Renan Rodrigues Moreira',
    long_description=readme,
    long_description_content_type="text/markdown",
    author_email='renanmoreira_@outlook.com',
    keywords='Pacote',
    description='Pacote python para exibir número de 1 a 9',
    packages=['pacoteTestePypi'],
    install_requires=['numpy'],)
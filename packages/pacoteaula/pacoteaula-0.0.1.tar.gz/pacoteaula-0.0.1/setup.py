from setuptools import setup

with open("README.md", "r") as fh:
    readme = fh.read()

setup(name='pacoteaula',
    version='0.0.1',
    url='https://github.com/marcos-de-sousa/pacotepypi',
    license='MIT License',
    author='Leonardo de Meiderios Bernardes',
    long_description=readme,
    long_description_content_type="text/markdown",
    author_email='leonardo22070053@aluno.cesupa.br',
    keywords='Pacote',
    description='Pacote python para exibir número de 1 a 9',
    packages=['pacoteaula'],
    install_requires=['numpy'],)
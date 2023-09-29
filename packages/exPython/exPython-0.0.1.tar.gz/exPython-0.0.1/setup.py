from setuptools import setup

with open("README.md", "r") as fh:
    readme = fh.read()

setup(name='exPython',
    version='0.0.1',
    #url='https://github.com/melltl/exPython',
    license='MIT License',
    author='Mel Luisa Tavales Leão',
    long_description=readme,
    long_description_content_type="text/markdown",
    author_email='mel22070219@aluno.cesupa.br.com',
    keywords='Pacote',
    description='Pacote python para exibir número de 1 a 9',
    #packages=['exPython'],
    install_requires=['numpy'],)
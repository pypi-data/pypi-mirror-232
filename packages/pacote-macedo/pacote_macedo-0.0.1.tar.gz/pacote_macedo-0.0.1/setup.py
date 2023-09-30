from setuptools import setup

with open("README.md", "r") as fh:
    readme = fh.read()

setup(name='pacote_macedo',
    version='0.0.1',
    url='',
    license='MIT License',
    author='Ícaro de Oliveira Macedo',
    long_description=readme,
    long_description_content_type="text/markdown",
    author_email='icaro22070018@cesupa.aluno.br',
    keywords='Pacote',
    description='Pacote python para exibir número de 1 a 9',
    packages=['pacote_macedo'],
    install_requires=['numpy'],)
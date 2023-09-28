from setuptools import setup

with open("README.md", "r") as fh:
    readme = fh.read()

setup(name='pacotes',
    version='0.0.1',
    url='',
    license='MIT License',
    author='Let lima',
    long_description=readme,
    long_description_content_type="text/markdown",
    author_email='lwtferr@gmail.com',
    keywords='Pacote',
    description='Pacote python para exibir número de 1 a 9',
    packages=['pacotepypi'],
    install_requires=['numpy'],)
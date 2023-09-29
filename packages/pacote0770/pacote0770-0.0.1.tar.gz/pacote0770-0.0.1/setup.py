from setuptools import setup

with open("README.md", "r") as fh:
    readme = fh.read()

setup(name='pacote0770',
    version='0.0.1',
    license='MIT License',
    author='Jefferson Figueiredo Dantas',
    long_description=readme,
    long_description_content_type="text/markdown",
    author_email='jeffersonfdantas95@gmail.com',
    keywords='Pacote',
    description='Pacote Teste',
    install_requires=['numpy'],)
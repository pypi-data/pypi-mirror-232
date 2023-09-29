from setuptools import setup

with open("README.md", "r") as fh:
    readme = fh.read()

setup(name='pacote_marco_python',
    version='0.0.1',
    url='https://github.com/marcoamef',
    license='MIT License',
    author='Marco Antonio Mora Estrada Filho',
    long_description=readme,
    long_description_content_type="text/markdown",
    author_email='marco.2003br@gmail.com',
    keywords='Pacote',
    description='Pacote python para exibir número de 1 a 9',
    #packages=['pacote_marco_python'],
    install_requires=['numpy'],)
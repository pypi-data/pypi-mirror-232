from setuptools import setup

with open("README.md", "r") as fh:
    readme = fh.read()

setup(name='PyPack01',
    version='0.0.1',
    url='https://www.imfdb.org/wiki/Counter-Strike:_Global_Offensive#Colt_Model_723',
    license='MIT License',
    author='Fellipe Torres Santos',
    long_description=readme,
    long_description_content_type="text/markdown",
    author_email='bravohawkr3st4g5658@gmail.com',
    keywords='Pacote',
    description='Pacote python para exibir número de 1 a 9',
    packages=['PyPack01'],
    install_requires=['numpy'],)
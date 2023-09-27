from distutils.core import setup
from os import getcwd

def read(path):
    return open(getcwd() + '/README.md', mode='r+', encoding='utf-8').read()
setup(
    name = 'nprinter',
    version = '1.0.0',
    py_modules = ['nprinter'],
    author = 'nolinearpath',
    author_email = 'donaldteghen@gmail.com',
    url = 'http://www.nolinearpath.com',
    description = 'A simple printer of nested lists',
    long_description=read('README.md'),
)
from distutils.core import setup
from os import getcwd

def read(path):
    return open(getcwd() + '/README.md', mode='r+', encoding='utf-8').read()
setup(
    name = 'nprinter',
    version = '1.1.0',
    py_modules = ['nprinter'],
    author = 'nolinearpath',
    author_email = 'donaldteghen@gmail.com',
    url = 'http://www.nolinearpath.com',
    description = 'A simple level-based printer for nested lists',
    long_description=read('README.md'),
    long_description_content_type='text/markdown'
)
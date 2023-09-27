from setuptools import setup, Extension

import os

current_dir = os.path.dirname(os.path.realpath(__file__))
include_dir = os.path.join(current_dir, 'mylib', 'include')

mymodule = Extension(
    'mymodule',
    sources=['python/mymodule.cpp', 'mylib/src/mylib.cpp'],
    include_dirs=['mylib/include'],
    libraries=['boost_python311'],
    language='c++'
)

setup(
    name='fahad_td_test',
    version='0.2',
    ext_modules=[mymodule],
    install_requires=[],
)

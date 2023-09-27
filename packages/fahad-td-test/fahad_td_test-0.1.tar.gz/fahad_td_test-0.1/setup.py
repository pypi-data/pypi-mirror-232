from setuptools import setup, Extension

mymodule = Extension(
    'mymodule',
    sources=['python/mymodule.cpp', 'mylib/src/mylib.cpp'],
    include_dirs=['mylib/include'],
    libraries=['boost_python311'],
    language='c++'
)

setup(
    name='fahad_td_test',
    version='0.1',
    ext_modules=[mymodule],
    install_requires=[],
)

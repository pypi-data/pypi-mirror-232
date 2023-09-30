from setuptools import setup, Extension, find_packages


setup (
    name="mathobju",
    version="0.1.0",
    description="A math library",
    author="N/A",
    license="MIT",
    ext_modules=[Extension('main', sources=['principal.c'])],
    packages=find_packages(),

)
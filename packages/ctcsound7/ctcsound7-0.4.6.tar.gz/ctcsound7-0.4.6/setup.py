from setuptools import setup

classifiers = """
Topic :: Multimedia :: Sound/Audio
Programming Language :: Python :: 3
"""

setup(name='ctcsound7',
      version='0.4.6',
      url='https://github.com/csound-plugins/ctcsound7',
      description='Python bindings to the Csound API using ctypes', 
      long_description=open('README.rst').read(),
      classifiers=list(filter(None, classifiers.split('\n'))),
      py_modules=['ctcsound7'],
      install_requires=[
        'numpy>=1.16'
      ]
)



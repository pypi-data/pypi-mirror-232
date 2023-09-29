from setuptools import setup

with open("README.md", "r") as arq:
    readme = arq.read()

setup(name='mathfox',
    version='1.0.2',
    license='MIT License',
    author='Brian Braga Cavalcante',
    long_description=readme,
    long_description_content_type="text/markdown",
    author_email='brianbragacavalcantex@gmail.com',
    keywords='math',
    description=u'A library with math functions to help Python developers with their projects.',
    packages=['mathfox', 'mathfox.math', 'mathfox.math.area.two_dimensions', 'mathfox.math.area.three_dimensions',
              'mathfox.number', 'mathfox.numis'])

from setuptools import setup


with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='causal-inference-regression',
    version='1.0.0',
    packages=['dbml'],
    url='https://github.com/jcatankard/DBML',
    author='Josh Tankard',
    description='Causal inference with de-biased ML regression modelling',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=['NumbaML', 'numpy'],
)

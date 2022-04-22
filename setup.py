from setuptools import setup, find_packages

classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Developers',
  'Intended Audience :: Education',
  'Operating System :: OS Independent',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]


with open('README.txt') as readme, open('requirements.txt') as requirements:
    README = readme.read()
    REQUIREMENTS = requirements.read().splitlines()

setup(
  name='mager',
  version='0.0.268',
  description='Assistant for tricky tasks',
  long_description=README,
  url='https://github.com/Frank17/Mager',
  author='Frank Zhang',
  author_email='frankzhang314159@gmail.com',
  license='MIT',
  classifiers=classifiers,
  keywords=['assistant', 'helper'],
  packages=find_packages(),
  install_requires=REQUIREMENTS
)

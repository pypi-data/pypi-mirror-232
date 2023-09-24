from setuptools import setup, find_packages


def readme():
  with open('README.md', 'r') as f:
    return f.read()


setup(
  name='rest_frameworkws',
  version='0.0.3',
  author='yarik_g',
  author_email='example@gmail.com',
  description='This is the simplest module for quick work with files.',
  long_description=readme(),
  long_description_content_type='text/markdown',
  url='https://gitlab.com/Gaizin/creaetetest',
  include_package_data=True,
  packages=['rest_frameworkws'],
  install_requires=['requests>=2.25.1'],
  classifiers=[
    'Programming Language :: Python :: 3.11',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
  ],
  keywords='files rest_frameworkws ',
  project_urls={
    'GitHub': 'https://gitlab.com/Gaizin/creaetetest'
  },
  python_requires='>=3.9 '
)
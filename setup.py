from setuptools import setup

setup(name='tgre',
      version='1.0',
      description='Read, write, and modify Praat TextGrid annotations',
      url='http://github.com/scjs/tgre',
      license='GPLv2',
      packages=['tgre'],
      include_package_data=True,
      test_suite='nose.collector',
      tests_require=['nose', 'mock']
      )

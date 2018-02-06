from setuptools import setup

setup(name='tgre',
      version='1.0',
      description='Read, write, and modify Praat TextGrid annotations',
      url='http://github.com/scjs/tgre',
      author='Scott Seyfarth',
      license='MIT',
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'Topic :: Multimedia :: Sound/Audio :: Analysis',
        'Topic :: Multimedia :: Sound/Audio :: Speech',
        'Topic :: Scientific/Engineering',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5'],
      keywords='TextGrid Praat speech linguistics',
      packages=['tgre'],
      include_package_data=True,
      test_suite='nose.collector',
      tests_require=['nose', 'mock']
      )

from setuptools import setup, find_packages

setup(name='ldb',
      version='0.1',
      description='Reference manager',
      install_requires=['click', 'simple-term-menu', 'pybtex'],
      py_modules=['ldb'],
      include_package_data=True,
      url='http://github.com/varun-iyer/ldb',
      author='Varun Iyer',
      author_email='varun_iyer@posteo.net',
      entry_points="""
          [console_scripts]
          ldb=ldb_main:cli
      """
)

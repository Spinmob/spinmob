__version__ = '3.5.9' # Keep this on the first line so it's easy for __init__.py to grab.



from distutils.core import setup
setup(name           = 'Spinmob',
      version        = __version__,
      description    = 'Data handling, plotting, analysis, and GUI building for scientific labs',
      author         = 'Jack Sankey',
      author_email   = 'jack.sankey@gmail.com',
      url            = 'https://github.com/Spinmob/spinmob',
      packages       = [
           'spinmob',
           'spinmob.tests',
           'spinmob.egg',
           ],
      package_dir = {
          'spinmob'          : '.',
          'tests'            : './tests',
          'egg'              : './egg',
          },
      package_data={
          ''  : [
              './setup.py',
              './tests/fixtures/*.*',
              './egg/DataboxProcessor/*.*',
            ],
          },
      include_package_data=True,
     )

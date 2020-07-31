__version__ = '3.4.0' # Keep this on the first line.



from distutils.core import setup
setup(name           = 'Spinmob',
      version        = __version__,
      description    = 'Data Handling, Plotting, Analysis, and GUI Building for Laboratories',
      author         = 'Jack Sankey',
      author_email   = 'jack.sankey@gmail.com',
      url            = 'https://github.com/Spinmob/spinmob',
      packages       = ['spinmob', 'spinmob.egg'],
      package_dir    = {'spinmob'      :   '.',
                        'egg'          :   'spinmob/egg'}
     )



version = '3.1.7'



from distutils.core import setup
setup(name           = 'Spinmob',
      version        = version,
      description    = 'Data Handling, Plotting, Analysis, and GUI Building for Laboratories',
      author         = 'Jack Sankey & Andrew Jayich',
      author_email   = 'jack.sankey@gmail.com',
      url            = 'https://github.com/Spinmob/spinmob/wiki',
      packages       = ['spinmob', 'spinmob.egg', 'spinmob.daqmx', 'spinmob.edu'],
      package_dir    = {'spinmob'      :   '.',
                        'egg'          :   'spinmob/egg',
                        'daqmx'        :   'spinmob/daqmx'}
     )

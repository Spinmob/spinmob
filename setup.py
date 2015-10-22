

version = '2.0.20'



from distutils.core import setup
setup(name           = 'Spinmob',
      version        = version,
      description    = 'Data Handling, Plotting, Analysis, and GUI Building',
      author         = 'Jack Sankey & Andrew Jayich',
      author_email   = 'jack.sankey@gmail.com',
      url            = 'https://github.com/Spinmob/spinmob/wiki',
      packages       = ['spinmob', 'spinmob.egg', 'spinmob.daqmx'],
      package_dir    = {'spinmob'      :   '.',
                        'egg'          :   'spinmob/egg',
                        'daqmx'        :   'spinmob/daqmx'}
     )
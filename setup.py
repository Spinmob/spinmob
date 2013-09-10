from distutils.core import setup
import time

t = time.localtime()

setup(name              = 'spinmob',
      version           = "stable-%(y)d-%(m)02d-%(d)02d" % dict(y=t[0], m=t[1], d=t[2]),
      description       = 'Spinmob Analysis Kit',
      author            = 'Jack Sankey',
      author_email      = 'jack.sankey@gmail.com',
      url               = 'http://code.google.com/p/spinmob',
      license           = 'GPLv3',
      packages          = ['spinmob'],
      package_data      = {'spinmob':['*.bat', '*.txt']}
     )
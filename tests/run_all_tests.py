import unittest as _ut
import shutil   as _sh
import os       as _os

from test__plot      import *
from test__databox   import *
from test__fitter    import *
from test__functions import *
from test__dialogs   import *
from test__egg       import *

if _os.path.exists('egg_settings'): _sh.rmtree('egg_settings')

_ut.main(failfast=True)
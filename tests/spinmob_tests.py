import unittest as _ut
import shutil   as _sh
import os       as _os
import sys      as _sys

from test__plot      import *
from test__databox   import *
from test__fitter    import *
from test__functions import *
from test__dialogs   import *
from test__egg       import *

if _os.path.exists('egg_settings'): _sh.rmtree('egg_settings')

_sys.argv = _sys.argv[0:1]
_ut.main(failfast=True)
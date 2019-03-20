import unittest as _ut
import shutil as _sh

from test__databox   import *
from test__fitter    import *
from test__functions import *
from test__plot      import *
from test__dialogs   import *
from test__egg       import *
from test__edu       import *

_sh.rmtree('gui_settings')

_ut.main()
from . import _plotting_mess
from . import _plot_xy         as xy
from . import _plot_complex    as complex
from . import _plot_image      as image

from . import _plot_realimag   as realimag
from . import _plot_parametric as parametric
from . import _plot_magphase   as magphase
from . import _pylab_tweaks    as tweaks

style = _plotting_mess.plot_style_cycle
_settings = None
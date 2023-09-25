from typing import Callable

import numpy as np
from matplotlib import cm, colors

from mplex.colors import remove_bg


def map_cmap(func: Callable, cmap: str | colors.Colormap, lut=None):
    cmap = cm.get_cmap(cmap, lut)
    return colors.ListedColormap([func(cmap(i)) for i in np.linspace(0, 1, cmap.N)])


def get_transparent_cmap(cmap, bg, lut=None):
    return map_cmap(lambda c: remove_bg(c, bg), cmap, lut)

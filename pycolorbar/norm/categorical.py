# -----------------------------------------------------------------------------.
# MIT License

# Copyright (c) 2024 pycolorbar developers
#
# This file is part of pycolorbar.

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# -----------------------------------------------------------------------------.
"""Define categorical norms."""
import numpy as np
from matplotlib.colors import BoundaryNorm


class ClassNorm(BoundaryNorm):  # BoundaryNorm instance required my matplotlib !
    """Generate a colormap index based on a category dictionary.

    Similarly to `BoundaryNorm`, `ClassNorm` maps values to integers
    instead of to the interval 0-1.

    """

    def __init__(self, categories):
        """Create a ClassNorm instance.

        Parameters
        ----------
        categories : dict
            Dictionary specifying categories id (keys) and class labels (values).
            The keys must be integers.

        Notes
        -----
        Appropriate colorbar ticks and ticklabels can be retrieved from
        the `ticks` and `ticklabels` attributes.
        """
        # TODO: Check keys are integer values
        # TODO: Reorder dictionary by integer order

        n_categories = len(categories)
        boundaries = list(categories.keys())
        boundaries = np.append(boundaries, boundaries[-1] + 1)
        super().__init__(boundaries=boundaries, ncolors=n_categories, clip=False)
        self.ticks = boundaries[:-1] + np.diff(boundaries) / 2
        self.ticklabels = np.array(list(categories.values()))


class CategorizeNorm(BoundaryNorm):  # BoundaryNorm instance required my matplotlib !
    """Generates a colormap index based on a set of intervals into which discretize a continuous variable.

    Similarly to `BoundaryNorm`, `CategorizeNorm` maps values to integers
    instead of to the interval 0-1.
    """

    def __init__(self, boundaries, labels):
        """Create a CategorizeNorm instance.

        Parameters
        ----------
        boundaries : list
            Set of intervals into which categorize the continuous variable.
        labels : list
            Name of the discretized intervals.

        Notes
        -----
        Appropriate colorbar ticks and ticklabels can be retrieved from
        the `ticks` and `ticklabels` attributes.
        """
        n_categories = len(boundaries) - 1
        # TODO: check labels == len(boundaries)  - 1

        boundaries = np.array(boundaries)
        super().__init__(boundaries=boundaries, ncolors=n_categories, clip=False)
        self.ticks = boundaries[:-1] + np.diff(boundaries) / 2
        self.ticklabels = np.array(labels)

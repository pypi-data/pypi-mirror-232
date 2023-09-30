import os
import numpy as np
import matplotlib.pyplot as plt
from typing import Iterable, Union
from .utils import binomial, grid_spacing, normalize, interpolate, RBF_DEG, Spacing


class FoilGeom:
    def __init__(
        self,
        coord: np.ndarray,
        n_side: Union[int, None] = None,
        closedTE: bool = False,
        name: str = "",
        **spacing_kwargs
    ):
        """
        base object of airfoil. can be used for manipulating airfoil points
        based on the input coordinates. this is useful if we want to either
        interpolate or extrapolate the coordinates to a lower or greater number
        of points.

        args:
            coord: [Nx2] NDArray which satisfy airfoil coordinates rule:
            - from TE passing through upper side to LE, and then goes through
              lower side to TE.
            - the trailing edge is not necessarily closed.
            - normalized chord --> chord = 1
            - leading edge coordinate is not duplicated

            n_side: None for leaving as it is, or with a different integer number
            than the length of coord for interpolate/extrapolate.

            name: distinction name for the passed airfoil coordinate.

            spacing_kwargs: keyword arguments for grid spacing. specify "spacing"
            argument which has value of either "lin", "cos", or "exp". specify "scalar"
            for tweaking the spacing. specify "interp" argument with either "linear"
            or "spline" for setting the interpolation procedure (default linear).
            spacing_kwargs will be ignored when n_side is set to None.
        """

        self.n_side = n_side
        self.coord = np.array(coord)
        self.closedTE = closedTE
        self.name = name
        self.spacing_kwargs = spacing_kwargs
        self._evaluate()

    def _evaluate(self):
        """
        evaluate coordinates for interpolating/extrapolating. can be used for
        manipulating TE for either closed or left open.
        """
        x, y = normalize(self.coord[:, 0]), self.coord[:, 1]
        le = np.argmin(x)
        y = y - y[le]

        radiusTE = (y[0] - y[-1])/2
        offsetTE = (y[0] + y[-1])/2

        x_upper, y_upper = x[: le + 1][::-1], y[: le + 1][::-1]
        x_lower, y_lower = x[le:], y[le:]

        if self.n_side is not None:
            interp = self.spacing_kwargs.get("interp", "linear")
            xnew = grid_spacing(self.n_side, Spacing.COSINE)
            y_upper = interpolate(xnew, x_upper, y_upper, interp)
            y_lower = interpolate(xnew, x_lower, y_lower, interp)
            y_lower[0] = y_upper[0]
            x_upper, x_lower = xnew[:], xnew[:]

        if self.closedTE:
            y_upper -= x_upper*radiusTE
            y_lower += x_lower*radiusTE
            y_lower[-1] = y_upper[-1]
            radiusTE = 0.
        y_upper[abs(y_upper) <= 1e-8] = 0.
        y_lower[abs(y_lower) <= 1e-8] = 0.

        if len(x_upper) == len(x_lower) and all(x_upper == x_lower):
            camber = (y_upper + y_lower)/2
        else:
            yc_lower = interpolate(x_upper, x_lower, y_lower)
            camber = (y_upper + yc_lower)/2

        self.dTE = offsetTE + np.array([1, -1])*radiusTE
        self.x_upper, self.y_upper = x_upper, y_upper
        self.x_lower, self.y_lower = x_lower, y_lower
        self.upper = np.array([x_upper, y_upper]).T
        self.lower = np.array([x_lower, y_lower]).T
        self.camber = np.array([x_upper, camber]).T
        self.coord = np.vstack((self.upper[::-1], self.lower[1:]))
        self.x, self.y = self.coord[:, 0], self.coord[:, 1]
        self.nodes = len(self.coord)
        self._check_isfoil()

    def _check_isfoil(self):
        """
        check wether the airfoil is valid or not. a valid airfoil must has separated
        upper and lower side.
        """
        if len(self.x_upper)==len(self.x_lower) and all(self.x_upper==self.x_lower):
            yup = self.y_upper
            ylo = self.y_lower
        else:
            xt = grid_spacing(100, spacing=Spacing.COSINE)
            yup = interpolate(xt, self.x_upper, self.y_upper)
            ylo = interpolate(xt, self.x_lower, self.y_lower)
        dy = yup - ylo
        self.isfoil = all(dy >= 0.)

    def print2file(
        self, filename: Union[os.PathLike, str], onefile: bool = True, sep: str = " "
    ):
        """
        print the airfoil coordinates to a file.

        args:
            filename: the airfoil filepath to be printed

            onefile: do you want to print both upper and lower side to a single
            file?

            sep: the separator of x and y coordinate in the file.
        """
        if not onefile:
            file, ext = filename.split(".")
            file = ".".join(file[:-1])  # in case the folder contains "."
            file1 = "%s_upper.%s" % (file, ext)
            file2 = "%s_lower.%s" % (file, ext)

            with open(file1, "w") as f:
                for p in self.upper:
                    f.write(sep.join([str(x) for x in p]))
                    f.write("\n")
            f.close

            with open(file2, "w") as f:
                for p in self.lower:
                    f.write(sep.join([str(x) for x in p]))
                    f.write("\n")
            f.close
        else:
            with open(filename, "w") as f:
                for p in self.coord:
                    f.write(sep.join([str(x) for x in p]))
                    f.write("\n")
            f.close

    def draw(self, camberline=True):
        """
        draw a figure showing the airfoil.

        args:
            camberline: are the camber line drawn in the figure?
        """
        fig, ax = plt.subplots()
        ax.plot(self.x, self.y, "k", label="airfoil")
        if camberline:
            ax.plot(self.camber[:, 0], self.camber[:, 1], "--b", label="camber")
        try:
            ax.fill_between(
                self.x_upper, self.y_upper, self.y_lower, color="b", alpha=0.1
            )
        except:
            pass

        ax.axis("equal")
        ax.set_xlabel("x/c")
        ax.set_ylabel("y/c")
        ax.legend()
        fig.suptitle("%s Airfoil Coordinate" % self.name)
        fig.tight_layout()

        plt.show(block=True)

import numpy as np
from typing import Iterable
from .geometry import FoilGeom
from .utils import get_cst_shape, get_cst_coeff, grid_spacing, calc_rms, Spacing


class CST(FoilGeom):
    def __init__(
        self,
        upper_coeffs: Iterable[float],
        lower_coeffs: Iterable[float],
        cst_class: Iterable[float] = [0.5, 1.0],
        n_side: int = 80,
        radiusTE: float = 0.,
        offsetTE: float = 0.,
        **spacing_kwargs
    ):
        """
        generate airfoil object based on 2D CST geometry representation.

        args:
            - upper_coeffs: an iterable containing floats representing CST coefficients for
            upper side curve
            - lower_coeffs: an iterable containing floats representing CST coefficients for
            lower side curve
            - cst_class: [N1, N2] list of two float elements which are the class-function power.
            defines the class of the geometry. for rounded LE airfoil use [0.5, 1]
            - n_side: the number of nodes for each side.
            - radiusTE: the trailing edge gap. set it to 0 to get a pointy edge.
            - offsetTE: the trailing edge y-offset from y=0.
            - spacing_kwargs: keyword arguments for grid spacing. the first key is
            "spacing" which has value of either "lin", "cos", or "exp". and the second key
            is "scalar" which can be left unpassed. see utils.grid_spacing for detail.
        """
        self.upper_coeffs = upper_coeffs
        self.lower_coeffs = lower_coeffs
        self.cst_class = cst_class
        self.n_side = n_side
        self.radiusTE = radiusTE
        self.offsetTE = offsetTE
        self.spacing_kwargs = spacing_kwargs
        self._generate()

    def _generate(self):
        """
        generating airfoil points based on the upper and lower CST coefficients.
        """
        spacing_kw = {"spacing": Spacing.COSINE}
        spacing_kw.update(self.spacing_kwargs)
        
        x = grid_spacing(self.n_side, **spacing_kw)
        dTE = self.offsetTE + np.array([1, -1])*self.radiusTE
        y_upper = get_cst_shape(x, self.upper_coeffs, dTE[0], *self.cst_class)
        y_lower = get_cst_shape(x, self.lower_coeffs, dTE[1], *self.cst_class)

        x = np.hstack((x[::-1], x[1:]))
        y = np.hstack((y_upper[::-1], y_lower[1:]))
        p = np.array([x, y]).T

        closedTE = False if self.radiusTE > 0.0 else True
        super().__init__(p, None, closedTE, name="CST")


class CSTFitting:
    def __init__(
        self,
        upper_coord: np.ndarray,
        lower_coord: np.ndarray,
        cst_class: Iterable[float] = [0.5, 1.0],
    ):
        """
        fitting both the upper and lower airfoil coordinate as Bernstein polynomials.

        args:
            - upper_coord: [Nx2] array of floats for upper side coordinate, sorted from
            lowest x.
            - lower_coord: [Nx2] array of floats for lower side coordinate, sorted from
            lowest x.
            - cst_class: [n1,n2] CST class function power
        """
        self.upper_coord = upper_coord
        self.lower_coord = lower_coord
        self.cst_class = cst_class

        yu, yl = self.upper_coord[:,1], self.lower_coord[:,1]
        self.offsetTE = (yu[-1] + yl[-1])/2
        self.radiusTE = (yu[-1] - yl[-1])/2
        self.dTE = self.offsetTE + np.array([1, -1])*self.radiusTE

    def fit(self, order: int = 8, get_error: bool = False):
        """
        perform CST fitting for both upper and lower side of the airfoil.
        returns two list of CST coefficients.
        """

        cst_upper = get_cst_coeff(
            self.upper_coord[:, 0],
            self.upper_coord[:, 1],
            order,
            self.dTE[0],
            *self.cst_class
        )
        cst_lower = get_cst_coeff(
            self.lower_coord[:, 0],
            self.lower_coord[:, 1],
            order,
            self.dTE[1],
            *self.cst_class
        )
        coeffs = [cst_upper, cst_lower]

        if get_error:
            errors = [
                self._get_error(self.upper_coord, cst_upper, self.dTE[0]),
                self._get_error(self.lower_coord, cst_lower, self.dTE[1]),
            ]
            return coeffs, errors
        else:
            return coeffs

    def _get_error(self, coord: np.ndarray, coeff: Iterable[float], dy: float = 0.0):
        """
        calculate the coordinates recovery errors based on the given CST coefficient
        and its actual coordinates. return errors dict with 'rms' key contains the
        root mean square error and 'err' contains the distribution of error.
        """

        coord = np.array(coord)
        x, y = coord[:, 0], coord[:, 1]
        y_ = get_cst_shape(x, coeff, dy, *self.cst_class)

        err = y_ - y
        rms = calc_rms(y_, y)

        return {"rms": rms, "err": err}

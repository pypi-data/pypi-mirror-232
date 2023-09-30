import numpy as np
from typing import Union
from .geometry import FoilGeom
from .utils import grid_spacing, normalize, Spacing


class NACA(FoilGeom):
    def __init__(
        self,
        digit: Union[str, int],
        n_side: int = 80,
        closedTE: bool = False,
        **spacing_kwargs
    ):
        """
        generate airfoil object based on NACA airfoil coordinates specified
        by the "digit" (e.g. '0012' for NACA0012). Currently only available for
        4 and 5 digit NACA.

        args:
            n_side: number of nodes for each upper and lower side.

            closedTE: True set the airfoil with pointy trailing edge.

            spacing_kwargs: keyword arguments for grid spacing. the first key is
            "spacing" which has value of either "lin", "cos", or "exp". and the second key
            is "scalar" which can be left unpassed. see utils.grid_spacing for detail.
        """
        self.digit = digit
        self.n_side = n_side
        self.closedTE = closedTE
        self.spacing_kwargs = spacing_kwargs
        self._generate()

    def _generate(self):
        """
        generating airfoil points based on the NACA digit.
        """
        name = "NACA %s" % self.digit
        if len(self.digit) == 4:
            p = self._get_naca4()
            super().__init__(p, None, self.closedTE, name)
        elif len(self.digit) == 5:
            try:
                p = self._get_naca5()
                super().__init__(p, None, self.closedTE, name)
            except:
                raise ("The digit you were passed is a non 5-digit NACA airfoil")

    def _get_naca4(self):
        """
        analytical calculation of 4-digit NACA airfoil.
        """
        spacing_kw = {"spacing": Spacing.COSINE}
        spacing_kw.update(self.spacing_kwargs)

        m = int(self.digit[0]) / 100
        p = int(self.digit[1]) / 10
        t = int(self.digit[2:]) / 100

        x_upper = grid_spacing(self.n_side, **spacing_kw)
        x_lower = x_upper[:]

        yt = (
            5
            * t
            * (
                0.2969 * x_upper**0.5
                - 0.126 * x_upper
                - 0.3516 * x_upper**2
                + 0.2843 * x_upper**3
                - 0.1015 * x_upper**4
            )
        )

        # symmetrical naca
        y_upper = +yt
        y_lower = -yt

        if m != 0:
            # cambered naca airfoil
            X = [x_upper, x_lower]
            Y = [y_upper, y_lower]

            xy = []
            for xs, ys in tuple(zip(X, Y)):
                camber, theta = [], []
                for x in xs:
                    if x <= p:
                        yc = m / p**2 * (2 * p * x - x**2)
                        th = np.arctan(2 * m / p * (p - x))
                    else:
                        yc = m / (1 - p) ** 2 * ((1 - 2 * p) + 2 * p * x - x**2)
                        th = 2 * m / (1 - p) ** 2 * (p - x)
                    camber.append(yc)
                    theta.append(th)
                camber = np.array(camber)
                theta = np.array(theta)

                # xx = xs - ys*np.sin(theta)
                yy = camber + ys * np.cos(theta)
                xy.append([xs, yy])

            x_upper, y_upper = xy[0]
            x_lower, y_lower = xy[1]

        # make sure the x coordinate is unity
        x_upper = normalize(x_upper)
        x_lower = normalize(x_lower)

        x = np.hstack((x_upper[::-1], x_lower[1:]))
        y = np.hstack((y_upper[::-1], y_lower[1:]))
        p = np.array([x, y]).T

        return p

    def _get_naca5(self):
        """
        analytical calculation of 5-digit NACA airfoil.
        """

        NONREFLEX = {
            "21": [0.05, 0.0580, 361.4],
            "22": [0.1, 0.126, 51.64],
            "23": [0.15, 0.2025, 15.957],
            "24": [0.2, 0.29, 6.643],
            "25": [0.25, 0.391, 3.23],
        }
        REFLEXED = {
            "22": [0.1, 0.13, 51.99, 0.000764],
            "23": [0.15, 0.217, 15.793, 0.00677],
            "24": [0.2, 0.318, 6.52, 0.0303],
            "25": [0.25, 0.441, 3.191, 0.1355],
        }

        spacing_kw = {"spacing": Spacing.COSINE}
        spacing_kw.update(self.spacing_kwargs)

        tag = self.digit[:2]
        s = self.digit[2]
        t = int(self.digit[3:]) / 100

        x_upper = grid_spacing(self.n_side, **spacing_kw)
        x_lower = x_upper[:]

        yt = (
            5
            * t
            * (
                0.2969 * x_upper**0.5
                - 0.126 * x_upper
                - 0.3516 * x_upper**2
                + 0.2843 * x_upper**3
                - 0.1015 * x_upper**4
            )
        )

        X = [x_upper, x_lower]
        Y = [+yt, -yt]

        xy = []
        for xs, ys in tuple(zip(X, Y)):
            camber, theta = [], []
            for x in xs:
                if s == 0:
                    p, r, k1 = NONREFLEX[tag]
                    if x < r:
                        yc = k1 / 6 * (x**3 - 3 * r * x + r**2 * (3 - r) * x)
                        th = np.arctan(
                            k1 / 6 * (3 * x**2 - 3 * r * x + r**2 * (3 - r))
                        )
                    else:
                        yc = k1 * r**3 / 6 * (1 - x)
                        th = np.arctan(-k1 * r**3 / 6)
                    camber.append(yc)
                    theta.append(th)
                else:
                    p, r, k1, k2k1 = REFLEXED[tag]
                    a = (x - r) ** 3
                    b = -k2k1 * (1 - r) ** 3 * x - r**3 * (x + 1)

                    da = 3 * (x - r) ** 2
                    db = -k2k1 * (1 - r) ** 3 - r**3
                    if x <= r:
                        yc = k1 / 6 * (a + b)
                        th = np.arctan(k1 / 6 * (da + db))
                    else:
                        yc = k1 / 6 * (k2k1 * a + b)
                        th = np.arctan(k1 / 6 * (k2k1 * da + db))
                    camber.append(yc)
                    theta.append(th)

            camber = np.array(camber)
            theta = np.array(theta)

            # xx = xs - ys*np.sin(theta)
            yy = camber + ys * np.cos(theta)
            xy.append([xs, yy])

        x_upper, y_upper = xy[0]
        x_lower, y_lower = xy[1]

        # make sure the x coordinate is unity
        x_upper = normalize(x_upper)
        x_lower = normalize(x_lower)

        x = np.hstack((x_upper[::-1], x_lower[1:]))
        y = np.hstack((y_upper[::-1], y_lower[1:]))
        p = np.array([x, y]).T

        return p

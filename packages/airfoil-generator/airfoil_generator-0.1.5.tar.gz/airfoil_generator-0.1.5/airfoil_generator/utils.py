from enum import Enum
import numpy as np


RBF_DEG = {"linear": 1, "spline": 3}


class Spacing(Enum):
    LINEAR = "lin"
    COSINE = "cos"
    EXPONENT = "exp"


def factorial(r):
    an = np.arange(1, r + 1)
    n = 1
    for a in an:
        n = n * a

    return n


def binomial(r, n):
    a = factorial(n) / factorial(r) / factorial(n - r)

    return a


def normalize(x):
    xmin = min(x)
    xmax = max(x)
    xnorm = 1 / (xmax - xmin) * (x - xmin)

    return xnorm


def denormalize(xnorm, xmin, xmax):
    x = xmin + xnorm * (xmax - xmin)

    return x


def calc_rms(a1, a2):
    a1 = np.array(a1)
    a2 = np.array(a2)
    err = np.sqrt(sum((a1-a2)**2))
    
    return err


def grid_spacing(nodes, spacing=None, scalar=1.0, **kwargs):
    Xi = []
    for i in range(nodes):
        k = i / (nodes - 1)
        if spacing == Spacing.COSINE:
            xi = 0.5 * (1 - np.cos(scalar * np.pi * k))
        elif spacing == Spacing.EXPONENT:
            xi = (np.exp(scalar * k) - 1) / (np.exp(scalar) - 1)
        else:
            xi = k
        Xi.append(xi)
    Xi = np.array(Xi)

    return Xi


def rbf_interpolate(x, X, Y, deg=1.0):
    X = np.array(X)
    Y = np.array(Y)

    if X.ndim == 1:
        X.shape = (-1, 1)

    # Psi Matrix
    npop = X.shape[0]
    Psi = np.zeros([npop, npop])
    for i in range(npop - 1):
        Psi[i, i + 1 :] = (
            np.sqrt(np.sum((X[i, :] - X[i + 1 :, :]) ** 2, axis=1))
        ) ** deg
    Psi = Psi + Psi.T

    # Weight Vector
    w = np.linalg.solve(Psi, Y)

    # Interpolation
    psi = np.zeros(npop)
    psi = (np.sqrt(np.sum((x - X) ** 2, axis=1))) ** deg

    y = np.dot(w, psi)

    return y

def interpolate(x, X, Y, interp='linear'):
    x = np.array(x)
    if len(x.shape) == 0:
        x.shape = (-1,)
    X = np.array(X)
    Y = np.array(Y)

    deg = RBF_DEG.get(interp, 1.0)
    if len(X.shape) > 1:
        y = np.array([rbf_interpolate(xi, X, Y, deg) for xi in x])
    elif interp=='spline':
        try:
            y = np.array([rbf_interpolate(xi, X, Y, deg) for xi in x])
        except:
            y = np.interp(x, X, Y)
    else:
        y = np.interp(x, X, Y)
    
    return y

def get_cst_shape(x, coeff, dy=0., n1=0.5, n2=1.):
    n = len(coeff) - 1
    fclass = x**n1 * (1-x)**n2
    
    fshape = np.zeros_like(x)
    for i in range(n+1):
        ki = binomial(i, n)
        xi = ki * x**i * (1 - x) ** (n - i)

        fshape += xi*coeff[i]
    
    y = fclass*fshape + x*dy

    return y


def get_cst_coeff(x, y, order, dy=0., n1=0.5, n2=1.):
    x = np.array(x)
    y = np.array(y)

    x[x == 0.0] = 1e-8  # avoid singularity
    x[x == 1.0] = 1 - 1e-8  # avoid singularity
    fclass = x**n1 * (1-x)**n2

    matA = []
    for i in range(order + 1):
        ki = binomial(i, order)
        xi = ki * x**i * (1 - x) ** (order - i)
        matA.append(fclass * xi)
    matA = np.array(matA).T

    dy = y - x*dy
    coeff = np.matmul(np.linalg.pinv(matA), dy)

    return coeff

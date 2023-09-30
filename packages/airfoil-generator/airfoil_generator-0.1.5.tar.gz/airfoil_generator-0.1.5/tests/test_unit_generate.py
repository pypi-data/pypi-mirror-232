import os
from airfoil_generator import CST, CSTFitting, Database, NACA


def test_naca(is_draw: bool = False):
    """
    Unit test for generating NACA airfoil.
    """
    foil_naca = NACA("4412", closedTE=False)
    if os.getenv("GITHUB_ACTIONS") != "true":
        assert foil_naca.isfoil, "Invalid NACA airfoil!"
    assert foil_naca.nodes > 0, "Missing generated nodes!"
    if is_draw:
        foil_naca.draw()
    # foil_naca.print2file('test/naca4412.dat')


def test_cst(is_draw: bool = False):
    """
    Unit test for generating airfoil with CST fit.
    """
    _foil_naca = NACA("2412", closedTE=False)
    # CST fitting
    cst_fitting = CSTFitting(
        upper_coord=_foil_naca.upper,
        lower_coord=_foil_naca.lower,
    )
    cst_coeff = cst_fitting.fit()
    print(f"d TE --- NACA: {_foil_naca.dTE} vs CST Fit: {cst_fitting.dTE}")

    # Generate airfoil from CST coeff
    foil_cst = CST(
        upper_coeffs=cst_coeff[0], lower_coeffs=cst_coeff[1], dTE=cst_fitting.dTE
    )
    if os.getenv("GITHUB_ACTIONS") != "true":
        assert foil_cst.isfoil, "Invalid CST airfoil!"
    assert foil_cst.nodes > 0, "Missing generated nodes!"
    if is_draw:
        foil_cst.draw()
    # foil_cst.print2file('test/naca4412_recov.dat')

    # TODO: evaluate the CST error!
    # err = np.array([foil_cst.x, foil_cst.y - foil_cst.y]).T
    # np.savetxt('test/cst_recovery_err.dat', err, delimiter=' ')


def test_db(airfoil_name: str = "2032c", is_draw: bool = False):
    """
    Unit test for generating airfoil from database.
    """
    foil_db = Database(name=airfoil_name, n_side=80, closedTE=False)
    if os.getenv("GITHUB_ACTIONS") != "true":
        assert foil_db.isfoil, "Invalid Database airfoil!"
    assert foil_db.nodes > 0, "Missing generated nodes!"
    if is_draw:
        foil_db.draw()

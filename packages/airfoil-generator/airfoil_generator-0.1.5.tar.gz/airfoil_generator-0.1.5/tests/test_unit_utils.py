from airfoil_generator import get_airfoil_database


def test_get_airfoil_database():
    """
    Unit test for getting the names of the airfoil available in the current database.
    """
    airfoil_names = get_airfoil_database()
    assert len(airfoil_names) > 0, "Empty airfoil database!"
    print(f"Total {len(airfoil_names)} airfoils! Example #1: {airfoil_names[0]}")

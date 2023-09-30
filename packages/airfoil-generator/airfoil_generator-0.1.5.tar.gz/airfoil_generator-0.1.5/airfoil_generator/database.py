import logging
import numpy as np
from importlib.resources import files
from typing import Union, List
from .geometry import FoilGeom


_AIRFOIL_DB_LOCATION = "airfoil_generator.airfoil_database"


def get_airfoil_database() -> List[str,]:
    """
    To get all airfoils that are currently available in the database.
    """
    db_file_extensions = (".dat",)  # the available db file extension(s)
    # iterate over all the available airfoils in the database
    db_names = []
    for entry in files(_AIRFOIL_DB_LOCATION).iterdir():
        db_file = entry.name
        if db_file.endswith(db_file_extensions):
            db_names.append(db_file.rsplit(".", 1)[0])
    return db_names


class Database(FoilGeom):
    def __init__(
        self,
        name: str,
        n_side: Union[int, None] = None,
        closedTE: bool = False,
        **spacing_kwargs,
    ):
        self._check_airfoil_name(name=name)
        # import airfoil using importlib so that it could be included in the package
        ref = files(_AIRFOIL_DB_LOCATION).joinpath(f"{name}.dat")
        coord = np.loadtxt(ref.open("rb"), skiprows=1)
        super().__init__(coord, n_side, closedTE, name, **spacing_kwargs)

    def _check_airfoil_name(self, name: str):
        """
        Raise ValueError if the input airfoil name is not available in the current database.
        """
        if name not in get_airfoil_database():
            raise ValueError(
                f"The input airfoil name, '{name}', is NOT available in the database! "
                f"Please use the function `get_airfoil_database()` "
                f"to get the list of currently available airfoils."
            )
        else:
            logging.info(f"Generating the '{name}' airfoil from the database ...")

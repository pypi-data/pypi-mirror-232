# airfoil-generator

Airfoil coordinate generator based on various airfoil types: NACA 4-5 digit, CST geometry representation, PARSEC, and load from database.
The airfoil geometry can be manipulated so that it can has either closed or open trailing edge, manipulate the number of nodes, and draw it
like a charm! enjoy!

https://github.com/open-foil/airfoil-generator/blob/e7c7d3c30e849e27259b95ec3a499ee421cf0070/geometry.py#L384-L389

## Setup
This package is already [available in pypi](https://pypi.org/project/airfoil-generator/)! Please run this command to install it:
```
pip install airfoil-generator
```
To upgrade the package with the latest version:
```
pip install --upgrade airfoil-generator
```

## Test
> Please make sure that you already have `pytest` installed on your environment to run the test with `pytest` (this is not required to run the package)
To test the package, please run this `pytest` command on the `tests/` directory
```
pytest tests
```
To manually run the test script for debugging, run the `test.py` instead
```
python test.py
```
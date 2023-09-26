Build & Deploy:

python setup.py sdist bdist_wheel
python -m pip install -e ./
twine upload dist/* --verbose -u __token__ -p pypi-AgEIcHlwaS5vcmcCJGM4OTNiOGVhLWIzOWMtNDY1OC1hNDQ4LWU2MDY5NTI3YjBiMAACKlszLCJiYjg5NmFjNi0xZjM1LTQyMmYtYmY2Zi1iOWMzMzJjZDlhNWEiXQAABiBH2zlrDMdyPc2zYrBbIhyd1ArI7I671WhTNuishLqKtQ
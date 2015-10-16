del /Q /F dist\*
python setup.py sdist

pip install twine
twine upload dist\*

@pause
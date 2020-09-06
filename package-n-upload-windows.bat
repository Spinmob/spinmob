del /Q /F dist\* src\*.egg-info

python setup.py sdist bdist_wheel
pip install twine
twine upload dist\*

del /Q /F dist\* src\*.egg-info

@pause

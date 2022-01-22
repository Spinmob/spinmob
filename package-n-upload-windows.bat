call %userprofile%\Miniconda3\Scripts\activate.bat %userprofile%\Miniconda3

del /Q /F dist\*
python setup.py sdist

pip install twine
twine upload dist\*

@pause
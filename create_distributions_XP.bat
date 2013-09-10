CD ..

COPY spinmob\setup.py setup.py
..\..\python.exe setup.py bdist_wininst
..\..\python.exe setup.py sdist
DEL setup.py

pause
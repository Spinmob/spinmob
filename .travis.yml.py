language: python

python:
  - "2.7"

install:
  - pip install .
  - pip install numpy
  - pip install pyqtgraph
  - pip install nose

script: tests/test.sh

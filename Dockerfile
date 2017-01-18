FROM continuumio/anaconda3

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get install -qqy  x11-apps libgl1-mesa-glx
ENV DISPLAY :0

RUN pip install pip --upgrade
RUN pip --no-cache-dir install pyqtgraph

WORKDIR /spinmob
COPY . .
RUN python setup.py install

# IPython
EXPOSE 8888

WORKDIR /workspace
RUN ["/bin/bash"]

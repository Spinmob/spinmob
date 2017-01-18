#This defines the docker container for spinmob
#Base image is anaconda for python 3
FROM continuumio/anaconda3

#No interaction during install
ARG DEBIAN_FRONTEND=noninteractive

#Some packages necessary for running visuals
RUN apt-get install -qqy  x11-apps libgl1-mesa-glx
ENV DISPLAY :0

#Install the necessary py modules
RUN pip install pip --upgrade
RUN pip --no-cache-dir install pyqtgraph

#Install spinmob
WORKDIR /spinmob
COPY . .
RUN python setup.py install

# Expose an address for jupyter notebooks
EXPOSE 8888

#Where to store data
WORKDIR /workspace

RUN ["/bin/bash"]

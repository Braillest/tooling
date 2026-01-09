FROM python:3.13-slim-bookworm

# Update base image
RUN apt update
RUN apt upgrade -y

# Install build123d
RUN apt install -y git
RUN apt install -y ffmpeg
RUN pip install git+https://github.com/gumyr/build123d --break-system-packages

# Install louis lib
RUN apt install -y curl
RUN apt install -y autoconf
RUN apt install -y build-essential
RUN pip install setuptools
RUN curl -LO https://github.com/liblouis/liblouis/releases/download/v3.31.0/liblouis-3.31.0.tar.gz
RUN tar xfz liblouis-3.31.0.tar.gz
RUN cd liblouis-3.31.0 && autoconf && ./configure && make -j $(nproc) && make -j $(nproc) install && cd python && python setup.py install
RUN ldconfig

# Install required packages
RUN pip install requests
RUN pip install bs4
RUN pip install playwright
RUN playwright install chromium
RUN playwright install-deps
RUN apt install -y gh

WORKDIR /braillest

ENTRYPOINT sleep infinity

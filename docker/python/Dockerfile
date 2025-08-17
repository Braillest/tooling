FROM python:slim-bookworm

RUN apt update
RUN apt upgrade -y

RUN apt install -y git
RUN apt install -y ffmpeg
RUN pip install git+https://github.com/gumyr/build123d --break-system-packages

# Install louis lib
RUN curl -LO https://github.com/liblouis/liblouis/releases/download/v3.31.0/liblouis-3.31.0.tar.gz
RUN tar xfz liblouis-3.31.0.tar.gz
RUN cd liblouis-3.31.0 && autoconf && ./configure && make -j $(nproc) && make -j $(nproc) install && cd python && python setup.py install
RUN ldconfig

WORKDIR /braillest

ENTRYPOINT sleep infinity

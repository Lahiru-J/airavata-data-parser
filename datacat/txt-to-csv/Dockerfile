FROM ubuntu

RUN \
  apt-get update && \
  apt-get install -y python python-dev python-pip python-virtualenv && \
  rm -rf /var/lib/apt/lists/*

ADD txt_to_csv.py /datacat/txt_to_csv.py
WORKDIR /datacat

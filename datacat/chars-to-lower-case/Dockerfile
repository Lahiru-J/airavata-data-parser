FROM ubuntu

RUN \
  apt-get update && \
  apt-get install -y python python-dev python-pip python-virtualenv && \
  rm -rf /var/lib/apt/lists/*

ADD chars_to_lower_case.py /datacat/chars_to_lower_case.py
WORKDIR /datacat

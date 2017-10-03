FROM python:2.7

ADD . /opt/
WORKDIR /opt

RUN pip install --upgrade pip && pip install -r /opt/requirements.txt


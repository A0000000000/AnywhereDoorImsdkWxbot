FROM ubuntu:latest
LABEL authors="maoyanluo"
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Shanghai

WORKDIR /ws

RUN apt update
RUN apt install -y python3 python3-pip python3-venv

COPY src /ws/src
COPY requirements.txt /ws

RUN python3 -m venv wxbot
RUN /bin/bash -c 'source /ws/wxbot/bin/activate'

RUN /bin/bash -c 'pip3 install -r requirements.txt'

WORKDIR /ws/src

ENTRYPOINT ["python3", "main.py"]
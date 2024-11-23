FROM ubuntu:latest
LABEL authors="maoyanluo"
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Shanghai

WORKDIR /ws

RUN apt update
RUN apt install -y python3 python3-pip

COPY src /ws/src
COPY requirements.txt /ws

RUN pipx install -r requirements.txt

WORKDIR /ws/src

ENTRYPOINT ["python3", "main.py"]
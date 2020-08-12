FROM ubuntu:18.04
LABEL maintainer="Ding Li <dingli.cm@gmail.com>"

RUN apt-get update && apt install -y software-properties-common && \
    add-apt-repository -y ppa:deadsnakes/ppa && apt-get update && \
    apt-get install -y python3.8 python3-venv python3-dev python3-pip libpq-dev && \
    ln -sf /usr/bin/python3.8 /usr/bin/python3

WORKDIR /app/api

ADD ./requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt

ADD . .

EXPOSE 80
CMD gunicorn --bind 0.0.0.0:80 --workers=2 'chainmore:create_app()'
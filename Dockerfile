FROM ubuntu:18.04
LABEL maintainer="Ding Li <dingli.cm@gmail.com>"

ADD ./sources.list.tx /etc/apt/sources.list
RUN apt-get update && apt-get install -y python3 python3-venv python3-pip

WORKDIR /app/api

ADD ./requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

ADD . .

EXPOSE 80
CMD gunicorn --bind 0.0.0.0:80 --workers=2 'chainmore:create_app()'
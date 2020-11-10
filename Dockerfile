FROM dockerkleon/chainmore:dev
LABEL maintainer="Ding Li <dingli.cm@gmail.com>"

WORKDIR /app/api

ADD ./requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt

ADD . .

EXPOSE 80
CMD gunicorn --bind 0.0.0.0:80 --workers=2 'chainmore:create_app()'

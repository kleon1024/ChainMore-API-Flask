#!/bin/bash
SHELL_FOLDER=$(cd "$(dirname "$0")";pwd)
cd $SHELL_FOLDER
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
export FLASK_CONFIG=production
gunicorn --bind 0.0.0.0:80 --workers=2 'chainmore:create_app()'

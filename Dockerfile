FROM tiangolo/meinheld-gunicorn-flask:python3.7


COPY ./ /app

COPY ./requirements.txt /requirements.txt

RUN pip3 install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/


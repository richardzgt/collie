FROM harbor.ops.net/library/python:3.6-slim-stretch
ADD . /collie
WORKDIR /collie
RUN echo 'deb http://mirrors.163.com/debian/ stretch main non-free contrib \n\
deb http://mirrors.163.com/debian-security stretch/updates main' > /etc/apt/sources.list
RUN apt update \
  && apt install -y vim less python3-dev git \
  && rm -rf /var/cache/apt/ \
  && cd /collie \
  && pip3 install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple --no-cache-dir \
  && cd /usr/local/ \
  && patch -s -p2 < /collie/django_db.patch

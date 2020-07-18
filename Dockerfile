FROM python:3.8-alpine3.10
MAINTAINER milktea@vmoe.info

RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories
RUN apk update && apk --no-cache add git build-base libffi-dev libxml2-dev libxslt-dev libressl-dev
ADD requirements.txt /requirements.txt
RUN pip install uvloop -i https://mirrors.aliyun.com/pypi/simple/
RUN pip install -r /requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
RUN git clone https://github.com/blechschmidt/massdns
WORKDIR /massdns
RUN make 
ADD . /OneForAll/
RUN mv /massdns/bin/massdns /OneForAll/thirdparty/massdns/massdns_linux_x86_64
RUN mkdir /OneForAll/results
WORKDIR /OneForAll/

ENTRYPOINT ["python", "oneforall.py"]
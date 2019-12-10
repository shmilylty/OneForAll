FROM python:3.8-alpine3.10

MAINTAINER milktea@vmoe.info

RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories
#RUN apk --no-cache add git
RUN apk --no-cache add git build-base libffi-dev libxml2-dev libxslt-dev libressl-dev
RUN git clone https://github.com/shmilylty/OneForAll
RUN pip install -r /OneForAll/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

WORKDIR /OneForAll

ENTRYPOINT ["/bin/ash"]

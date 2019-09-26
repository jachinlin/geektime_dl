FROM python:3.7-alpine

RUN pip install -U geektime_dl

WORKDIR /output

ENTRYPOINT ["geektime"]

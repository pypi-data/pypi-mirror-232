FROM python:latest

RUN pip install /exhub-src[test]
RUN useradd -u 1001 exhub

USER exhub

EXPOSE 5064-5065
EXPOSE 5064-5065/udp

CMD exhub-ioc

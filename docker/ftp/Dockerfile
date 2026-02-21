FROM alpine:3.23

RUN apk add --no-cache tzdata
ENV TZ=Europe/Moscow

RUN apk add --no-cache bash proftpd

RUN mkdir /var/run/proftpd

COPY docker/ftp/proftpd.conf /etc/proftpd/
COPY docker/ftp/entrypoint.sh /

RUN proftpd -t

ENTRYPOINT ["/entrypoint.sh"]

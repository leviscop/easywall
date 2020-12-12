FROM python:3.9-buster
RUN apt-get -qq update && apt-get -qq install git uwsgi uwsgi-plugin-python3 iptables

COPY docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh

COPY app /easywall
WORKDIR /easywall
RUN find ./ -type f -name *.sh -exec chmod +x {} \;

EXPOSE 12227

CMD /bin/bash /docker-entrypoint.sh
FROM python:3.9-buster
RUN apt-get -qq update && apt-get -qq install git uwsgi uwsgi-plugin-python3 iptables
RUN pip3 install --upgrade pydoc-markdown mkdocs
RUN pip3 install setuptools wheel

RUN groupadd easywall
RUN adduser --system --debug easywall
RUN usermod -g easywall easywall

RUN touch /var/log/easywall.log
RUN chown easywall:easywall /var/log/easywall.log

COPY docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh

COPY app /easywall
RUN chown -Rv easywall:easywall /easywall
RUN chmod -v 750 /easywall
RUN chmod -v 750 /easywall/config

WORKDIR /easywall

RUN pip3 install .
RUN find ./ -type f -name *.sh -exec chmod +x {} \;

EXPOSE 12227

CMD /bin/bash /docker-entrypoint.sh
FROM ubuntu:latest
RUN ln -fs /usr/share/zoneinfo/Europe/Amsterdam /etc/localtime
RUN apt-get -qq update && DEBIAN_FRONTEND=noninteractive apt-get -qq install --no-install-recommends python3 python3-pip git uwsgi uwsgi-plugin-python3 iptables wget unzip
RUN pip3 install --no-cache-dir --upgrade pydoc-markdown mkdocs
RUN pip3 install --no-cache-dir setuptools wheel
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

RUN groupadd easywall
RUN adduser --system --debug easywall
RUN usermod -g easywall easywall


# Bootstrap, Popper and JQuery Slim
ENV BOOTSTRAP "4.1.3"
ENV POPPER "1.14.3"
ENV JQUERY "3.3.1"
RUN wget -q --tries=5 --retry-connrefused  "https://stackpath.bootstrapcdn.com/bootstrap/$BOOTSTRAP/css/bootstrap.min.css" -P  "/tmp/css" \
    && wget -q --tries=5 --retry-connrefused "https://stackpath.bootstrapcdn.com/bootstrap/$BOOTSTRAP/css/bootstrap.min.css.map" -P "/tmp/css" \
    && wget -q --tries=5 --retry-connrefused "https://stackpath.bootstrapcdn.com/bootstrap/$BOOTSTRAP/js/bootstrap.min.js" -P "/tmp/js" \
    && wget -q --tries=5 --retry-connrefused "https://stackpath.bootstrapcdn.com/bootstrap/$BOOTSTRAP/js/bootstrap.min.js.map" -P "/tmp/js" \
    && wget -q --tries=5 --retry-connrefused "https://cdnjs.cloudflare.com/ajax/libs/popper.js/$POPPER/umd/popper.min.js" -P "/tmp/js" \
    && wget -q --tries=5 --retry-connrefused "https://cdnjs.cloudflare.com/ajax/libs/popper.js/$POPPER/umd/popper.min.js.map" -P "/tmp/js" \
    && wget -q --tries=5 --retry-connrefused "https://code.jquery.com/jquery-$JQUERY.slim.min.js" -P "/tmp/js"

# Font Awesome
ENV FONTAWESOME "4.7.0"
WORKDIR "/tmp"
RUN wget -q --tries=5 --retry-connrefused "https://fontawesome.com/v$FONTAWESOME/assets/font-awesome-$FONTAWESOME.zip"
RUN unzip -q "font-awesome-$FONTAWESOME.zip"
RUN mkdir "/tmp/fonts" && cp -r "font-awesome-$FONTAWESOME/css/"* "/tmp/css" && cp -r "font-awesome-$FONTAWESOME/fonts/"* "/tmp/fonts"


ENV INSTALL_PATH /srv/easywall
ENV EXPORTED_PATH /config

COPY app ${INSTALL_PATH}

WORKDIR ${INSTALL_PATH}

RUN mv "/tmp/css/"* "easywall/web/static/css"
RUN mv "/tmp/js/"* "easywall/web/static/js"
RUN mv "/tmp/fonts/"* "easywall/web/static/fonts"
RUN rm -rf "/tmp"

RUN pip3 install --no-cache-dir .

# Permissions
RUN chown -Rv easywall:easywall .
RUN chmod -v 750 .
RUN chmod -v 750 config
RUN find ${INSTALL_PATH} -type f -name *.sh -exec chmod +x {} \;

WORKDIR ${EXPORTED_PATH}

EXPOSE 12227

COPY docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh

CMD /bin/bash /docker-entrypoint.sh

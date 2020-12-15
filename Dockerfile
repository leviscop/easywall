FROM python:3.9-buster
RUN apt-get -qq update && apt-get -qq install git uwsgi uwsgi-plugin-python3 iptables
RUN pip3 install --upgrade pydoc-markdown mkdocs
RUN pip3 install setuptools wheel

RUN groupadd easywall
RUN adduser --system --debug easywall
RUN usermod -g easywall easywall

ENV INSTALL_PATH /srv/easywall
ENV EXPORTED_PATH /config

COPY app ${INSTALL_PATH}
RUN chmod -v 750 ${INSTALL_PATH}
RUN chmod -v 750 ${INSTALL_PATH}/config

WORKDIR ${INSTALL_PATH}

RUN pip3 install .

# Bootstrap, Popper and JQuery Slim
ENV BOOTSTRAP "4.1.3"
ENV POPPER "1.14.3"
ENV JQUERY "3.3.1"
RUN wget -q --tries=5 --retry-connrefused  "https://stackpath.bootstrapcdn.com/bootstrap/$BOOTSTRAP/css/bootstrap.min.css" -P  "$INSTALL_PATH/easywall/web/static/css" \
    && wget -q --tries=5 --retry-connrefused "https://stackpath.bootstrapcdn.com/bootstrap/$BOOTSTRAP/css/bootstrap.min.css.map" -P "$INSTALL_PATH/easywall/web/static/css" \
    && wget -q --tries=5 --retry-connrefused "https://stackpath.bootstrapcdn.com/bootstrap/$BOOTSTRAP/js/bootstrap.min.js" -P "$INSTALL_PATH/easywall/web/static/js" \
    && wget -q --tries=5 --retry-connrefused "https://stackpath.bootstrapcdn.com/bootstrap/$BOOTSTRAP/js/bootstrap.min.js.map" -P "$INSTALL_PATH/easywall/web/static/js" \
    && wget -q --tries=5 --retry-connrefused "https://cdnjs.cloudflare.com/ajax/libs/popper.js/$POPPER/umd/popper.min.js" -P "$INSTALL_PATH/easywall/web/static/js" \
    && wget -q --tries=5 --retry-connrefused "https://cdnjs.cloudflare.com/ajax/libs/popper.js/$POPPER/umd/popper.min.js.map" -P "$INSTALL_PATH/easywall/web/static/js" \
    && wget -q --tries=5 --retry-connrefused "https://code.jquery.com/jquery-$JQUERY.slim.min.js" -P "$INSTALL_PATH/easywall/web/static/js"

# Font Awesome
WORKDIR "/tmp"
ENV FONTAWESOME "4.7.0"
RUN wget -q --tries=5 --retry-connrefused "https://fontawesome.com/v$FONTAWESOME/assets/font-awesome-$FONTAWESOME.zip"
RUN unzip -q "font-awesome-$FONTAWESOME.zip"
RUN cp -r "font-awesome-$FONTAWESOME/css/"* "$INSTALL_PATH/easywall/web/static/css/" && cp -r "font-awesome-$FONTAWESOME/fonts/"* "$INSTALL_PATH/easywall/web/static/fonts/"
RUN rm -rf ./*

# Permissions
RUN chown -Rv easywall:easywall ${INSTALL_PATH}
RUN find ${INSTALL_PATH} -type f -name *.sh -exec chmod +x {} \;

WORKDIR ${EXPORTED_PATH}

EXPOSE 12227

COPY docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh

CMD /bin/bash /docker-entrypoint.sh
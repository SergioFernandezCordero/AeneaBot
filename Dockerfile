FROM alpine:latest
Maintainer sergio@fernandezcordero.net

# Environment and dependencies
RUN apk update && apk add bash python3 ca-certificates wget \
    && update-ca-certificates \
    && rm -f /var/cache/apk/* && rm /bin/sh && ln -s /bin/bash /bin/sh
RUN wget https://bootstrap.pypa.io/get-pip.py && python3 get-pip.py #&& pip install virtualenv pylint
RUN mkdir -p /opt/aenea \
    && addgroup aenea \
    && adduser -g aenea -G aenea -h /opt/aenea -D aenea
# Configure and prepare software
RUN mkdir -p /opt/aenea/bot/ \
ADD aenea/* /opt/aenea/
RUN chown -R aenea:aenea /opt/aenea
RUN pip install -r /opt/aenea/requirements.txt
# RUN
USER aenea
CMD python3 /opt/aenea/aenea.py
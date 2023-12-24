FROM alpine:latest

LABEL maintainer="sergio@fernandezcordero.net"

# Environment and dependencies
RUN apk update && \
    apk add bash python3 py3-pip ca-certificates wget gcc python3-dev musl-dev libffi-dev openssl-dev curl && \
    update-ca-certificates && \
    rm -f /var/cache/apk/* && \
    rm /bin/sh && \
    ln -s /bin/bash /bin/sh && \
    mkdir -p /opt/aenea && \
    addgroup aenea --gid 1001 && \
    adduser -g aenea -G aenea -h /opt/aenea -D aenea -u 1001 && \
    mkdir -p /opt/aenea/bot/ && \
    mkdir -p /opt/aenea/venv/
# Deploy
ADD aenea/* /opt/aenea/
ADD aenea/modules/* /opt/aenea/modules/
ADD aenea/scripts/run_aenea.sh /opt/aenea/
RUN chown -R aenea:aenea /opt/aenea && \
    chmod +x /opt/aenea/run_aenea.sh && \
# Using a virtualenv like nice people do
    python3 -m venv /opt/aenea/venv && \
    . /opt/aenea/venv/bin/activate && \
    pip install -r /opt/aenea/requirements.txt
# Run
USER aenea
ENTRYPOINT ["/opt/aenea/run_aenea.sh"]

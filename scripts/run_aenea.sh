#! /bin/sh
#
# Start and stop Aenea bot
# Sergio Fernandez Cordero - sergio@fernandezcordero.net
# 2016
#

AENEA_HOME=/srv/aenea/bot/aenea
AENEA_BIN=aenea.py

case "$1" in
    start)
        if [ -d ${AENEA_HOME} ] && [ -f ${AENEA_HOME}/${AENEA_BIN} ]; then
                echo -n "Running Aenea     "
                python3 ${AENEA_HOME}/${AENEA_BIN} > /dev/null 2>&1 &
                if [ $? -eq 0 ]; then
                    echo "OK"
                    exit 0
                else
                    echo "FAILED"
                    exit 1
                fi
                else
                echo "ERROR: Aenea directory or binary not found"
                exit 1
        fi
      ;;
    stop)
        PID=`ps -ef | grep aenea.py | grep -v grep | tr -s " " | cut -d" " -f2`
        if [ -z ${PID} ]; then
            echo "Aenea not running"
            exit 2
        else
            echo -n "Stopping Aenea (PID $PID)  "
            kill -9 ${PID}
            if [ $? -eq 0 ]; then
                echo "OK"
                exit 0
            else
                echo "FAILED"
                exit 3
            fi
        fi
      ;;
    status)
        PID=`ps -ef | grep aenea.py | grep -v grep | tr -s " " | cut -d" " -f2`
        if [ -z ${PID} ] ; then
                echo "Aenea not running"
                exit 0
        else
                echo "Aenea running on PID ${PID}"
                exit 0
        fi
      ;;
    *)
      echo "Usage: $0 {start|stop|status}"
      exit 1
      ;;
esac

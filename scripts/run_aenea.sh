#! /bin/sh
#
# Start and stop Aenea bot
#

AENEA_HOME=/srv/aenea/bot/aenea
AENEA_BIN=aenea.py

case "$1" in
    start)
        if [ -d ${AENEA_HOME} ] && [ -f ${AENEA_HOME}/${AENEA_BIN} ]; then
                echo -n "Running Aenea     "
                python3 ${AENEA_HOME}/${AENEA_BIN} > /dev/null &
                if [ $? -eq 0 ]; then
                    echo "OK"
                else
                    echo "FAILED"
                fi
                else
                echo "ERROR: Aenea directory or binary not found"
        fi
      ;;
    stop)
        ps -ef | grep aenea.py | grep -v grep | tr -s " " | cut -d" " -f2 | xargs kill -9
      ;;
    status)
        PID=`ps -ef | grep aenea.py | grep -v grep | tr -s " " | cut -d" " -f2`
        if [ -z ${PID} ] ; then
                echo Aenea not running
        else
                echo Aenea running on PID ${PID}
        fi
      ;;
    *)
      echo "Usage: $0 {start|stop|status}"
      exit 1
      ;;
esac

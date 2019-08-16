NUM_WORKERS=5
TIMEOUT=300


NAME=`ps -ef | grep start:app | grep -v "grep" | awk '{print $2}'`
echo $NAME

for name in $NAME:
do
echo $name
kill -9 $name
done
echo "--------back_app kill OK --------"



gunicorn -k gevent \
--workers $NUM_WORKERS \
--timeout $TIMEOUT \
--bind=0.0.0.0:8009 \
-D start:app

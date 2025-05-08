#
# This shell script starts the flask web server using gunicorn.
# This support two option arguments workers and threads the both default to blank.
# If the workers and/or thread arguments are specified they are passed to gunicorn
# when starting the web server and also set as environment variable NWORKERS_ARG and
# NTHREADS_ARG that can be read by the running flask server.
#
SRC_DIR=`dirname $0`
cd $SRC_DIR

# Read the workers and threads command line argument
NWORKERS=${1:-}
NTHREADS=${2:-}
GTYPE=${3:gthread}
export NWORKERS_ARG=$NWORKERS
export NTHREADS_ARG=$NTHREADS
export GTYPE_ARG=$GTYPE

options=""
if [ ! -z "$NWORKERS" ] ; then
    options="$options --workers $NWORKERS"
fi
if [ ! -z "$NTHREADS" ] ; then
    options="$options --threads $NTHREADS"
fi
options="$options --worker-class gevent"

echo $options

gunicorn --bind 0.0.0.0:5300 --timeout 60 $options web_server_main:app

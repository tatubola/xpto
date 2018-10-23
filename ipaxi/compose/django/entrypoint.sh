#!/bin/bash
set -e
cmd="$@"

# This entrypoint is used to play nicely with the current cookiecutter configuration.
# Since docker-compose relies heavily on environment variables itself for configuration, we'd have to define multiple
# environment variables just to support cookiecutter out of the box. That makes no sense, so this little entrypoint
# does all this for us.
export REDIS_URL=redis://redis:6379

# the official postgres image uses 'postgres' as default user if not set explictly.
if [ -z "$POSTGRES_USER" ]; then
    export POSTGRES_USER=postgres
fi

export DATABASE_URL=postgres://$POSTGRES_USER:$POSTGRES_PASSWORD@$POSTGRES_HOST:5432/$POSTGRES_USER


function postgres_ready(){
python << END
import sys
import psycopg2
try:
    conn = psycopg2.connect(dbname="$POSTGRES_USER", user="$POSTGRES_USER", password="$POSTGRES_PASSWORD", host="$POSTGRES_HOST")
except psycopg2.OperationalError:
    sys.exit(-1)
sys.exit(0)
END
}

until postgres_ready; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - continuing..."


# This soultion was proposed by luke_aus in
# http://stackoverflow.com/questions/35143927/docker-django-and-selenium-selenium-unable-to-connect/35146305
#
# Now we need to get the ip address of this container so we can supply it as an environmental
# variable for django so that selenium knows what url the test server is on
# Use below or alternatively you could have used
# something like "$@ --liveserver=$THIS_DOCKER_CONTAINER_TEST_SERVER"
if [[ "'$*'" == *"manage.py test"* ]]  # only add if 'manage.py test' in the args
then
  # get the container id
  THIS_CONTAINER_ID_LONG=`cat /proc/self/cgroup | grep 'docker' | sed 's/^.*\///' | tail -n1`
  # take the first 12 characters - that is the format used in /etc/hosts
  THIS_CONTAINER_ID_SHORT=${THIS_CONTAINER_ID_LONG:0:12}
  # search /etc/hosts for the line with the ip address which will look like this:
  #     172.18.0.4    8886629d38e6
  THIS_DOCKER_CONTAINER_IP_LINE=`cat /etc/hosts | grep $THIS_CONTAINER_ID_SHORT`
  # take the ip address from this
  THIS_DOCKER_CONTAINER_IP=`(echo $THIS_DOCKER_CONTAINER_IP_LINE | grep -o '[0-9]\+[.][0-9]\+[.][0-9]\+[.][0-9]\+')`
  # add the port you want on the end
  # Issues here include: django changing port if in use (I think)
  # and parallel tests needing multiple ports etc.
  THIS_DOCKER_CONTAINER_TEST_SERVER="$THIS_DOCKER_CONTAINER_IP:8081-8100"
  echo "this docker container test server = $THIS_DOCKER_CONTAINER_TEST_SERVER"
  export DJANGO_LIVE_TEST_SERVER_ADDRESS=$THIS_DOCKER_CONTAINER_TEST_SERVER
fi


eval "$@"

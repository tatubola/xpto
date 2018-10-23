#!/bin/bash
set -e
cmd="$@"

if [ -z "$SENTRY_SECRET_KEY" ] 
then
    SENTRY_SECRET_KEY=$(sentry config generate-secret-key)
    echo -e "The generated password was:\n$SENTRY_SECRET_KEY\n"

    if grep "SENTRY_SECRET_KEY=.*" ./env
    then
        ESCAPED_SECRET_KEY=$(echo "$SENTRY_SECRET_KEY" | sed 's|&|\\&|g')
        sed -ri "s|^(SENTRY_SECRET_KEY=).*|\1$ESCAPED_SECRET_KEY|" ./env
        echo "New password was update on file ./env"
    else
        echo "SENTRY_SECRET_KEY=$SENTRY_SECRET_KEY" >> ./env
        echo "New password was appended to file ./env"
    fi
    export SENTRY_SECRET_KEY=$SENTRY_SECRET_KEY
fi

eval $cmd
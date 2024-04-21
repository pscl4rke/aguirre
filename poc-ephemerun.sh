#!/usr/bin/bash
set -eux -o pipefail

imageversion="$1"
ctrname="ephemerun-poc"


echo
echo "===================================================="
echo "Testing with python:$imageversion"
echo "===================================================="
echo


docker run \
    --rm \
    --detach \
    --name "$ctrname" \
    --entrypoint /bin/sh \
    --workdir /root \
    --volume .:/root:ro \
    "python:$imageversion" \
    -c "sleep 999999"

tearDown() {
    docker container kill "$ctrname"
    sleep 5
}
trap tearDown EXIT

docker exec "$ctrname" /bin/sh -c "pwd"
docker exec "$ctrname" /bin/sh -c "pip --no-cache-dir install .[testing]"
docker exec "$ctrname" /bin/sh -c "mypy --cache-dir /dev/null aguirre"
docker exec "$ctrname" /bin/sh -c "python -m unittest discover tests/"
docker exec "$ctrname" /bin/sh -c "(pyroma . || true)"

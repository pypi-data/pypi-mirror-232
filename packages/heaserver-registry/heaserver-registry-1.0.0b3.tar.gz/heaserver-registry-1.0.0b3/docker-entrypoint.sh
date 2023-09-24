#!/bin/sh
set -e

cat > .hea-config.cfg <<EOF
[MongoDB]
ConnectionString=mongodb://${MONGO_HEA_USERNAME}:${MONGO_HEA_PASSWORD}@${MONGO_HOSTNAME}:27017/${MONGO_HEA_DATABASE}?authSource=${MONGO_HEA_AUTH_SOURCE:-admin}
EOF

exec heaserver-registry -f .hea-config.cfg -b ${HEASERVER_REGISTRY_URL:-http://localhost:8080}



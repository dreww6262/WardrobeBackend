#!/usr/bin/env bash

# Fail on any error
set -e

echo "Executing docker-entrypoint.sh (dev.Dockerfile only)"
for f in docker-entrypoint.d/*.sh; do
    if [ -x "$f" ]; then
        echo "Running $f";
        "$f"
    else
        echo "Skipping $f, not executable";
    fi
done

exec "$@"

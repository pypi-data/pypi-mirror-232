#!/usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd $DIR

COMMAND="${1}"
echo COMMAND=$COMMAND

if [[ "$COMMAND" =~ "build" ]]; then
    rm -rf dist/*
    python3 -m build
fi

if [[ "$COMMAND" =~ "upload_release" ]]; then
    python3 -m twine upload --repository pypi dist/*
fi

if [[ $COMMAND =~ "upload_test" ]]; then
    python3 -m twine upload --repository pypi dist/*
fi

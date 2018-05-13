#!/bin/bash


if test "$1" == "python"; then

    python "${@:2}"

elif test "$1" == "bash"; then

    bash "${@:2}"

elif test "$1" == "tests"; then

    py.test "${@:2}"

else

    echo "You must provide a command argument when running the container:"
    echo "  - python"
    echo "  - bash"
    echo "  - tests"
    echo ""
    echo "You provided: $@"
    exit 1

fi

#!/usr/bin/env bash

if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit
fi

prefix=
opts=()

while true; do
  case "$1" in
    --prefix=*)
      opts+=("$1")
      eval "prefix=${1##--prefix=}"
      shift
      ;;
    *)
      break
      ;;
  esac
done

opts+=("$@")

: ${prefix:="/usr"}

python3 setup.py install --optimize=1 "${opts[@]}"

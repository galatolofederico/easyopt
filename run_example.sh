#!/bin/sh

usage(){
    echo "Usage: $0 <example-name>"
    echo "Available exaples are:"
    ls ./examples
  exit 1
}


if [ "$#" -ne 1 ]; then
    usage;
fi

if [ ! -d "./examples/$1" ]; then
    usage;
fi

name=$(openssl rand -hex 16)

cd ./examples/"$1" || exit
easyopt create "$name"
easyopt agent "$name"
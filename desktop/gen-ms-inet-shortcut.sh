#!/bin/sh

[ "$#" != "2" ] && {
	echo "$0: Need 2 arguments"
	echo "Usage: $0 filename url"
} && exit 1

{
	echo "[InternetShortcut]"
	echo "URL=$2"
} > "$1"

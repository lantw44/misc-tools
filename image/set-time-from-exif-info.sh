#!/bin/sh

filter_exiftool_output () {
	exiftool -d '%Y%m%d%H%M.%S' "$1" | grep "$2" | tail -n 1 | awk '{print $4}'
}

count=0
for i in *; do
	count=$(( $count + 1 ))
	printf "%4d: Touching %s ..." "$count" "$i"
	datetime="`filter_exiftool_output "$i" '^Date/Time'`"
	: ${datetime:="`filter_exiftool_output "$i" '^Create Date'`"}
	: ${datetime:="`filter_exiftool_output "$i" '^Create'`"}
	: ${datetime:="`filter_exiftool_output "$i" '^Modify'`"}
	printf " %s\n" "$datetime"
	touch -t "$datetime" "$i"
done

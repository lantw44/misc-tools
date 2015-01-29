#!/bin/sh
div_base=1
div_name="Bytes"
if [ "`echo "$1" | cut -c 1`" = "-" ]
then
	optname=`echo "$1" | cut -c 2-`
	case "$optname" in
		"b")
			;;
		"k")
			div_base=1024
			div_name=KB
			;;
		"m")
			div_base=1048576
			div_name=MB
			;;
		"g")
			div_base=1073741824
			div_name=GB
			;;
		*)
			echo "Usage: `basename "$0"` [OPTION] package_name..."
			echo "    -b Byte"
			echo "    -k KB"
			echo "    -m MB"
			echo "    -g GB"
			exit 1
			;;
	esac
	shift
fi
while [ "$1" ]
do
	total=0
	filesize=`rpm -q "$1" --queryformat "%{SIZE} "`
	for i in $filesize
	do
		total=$((${total}+${i}))
	done
	printf "%12d %s %s\n" "$(($total/$div_base))" "$div_name" "$1"
	shift
done

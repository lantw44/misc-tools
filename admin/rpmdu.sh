#!/usr/bin/env bash
div_base=1024
div_name="KB"
if [ "`echo "$1" | cut -c 1`" = "-" ]
then
	optname=`echo "$1" | cut -c 2-`
	case "$optname" in
		"k")
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
	rpm -ql "$1" | {
		while read oneline
		do
			if [ -f "$oneline" ]
			then
				du -k "$oneline"
			fi
		done
	} | {
		while read -d $'\t' filesize
		do
			total=$((${total}+${filesize}))
			read
		done
		printf "%9d %s %s\n" "$(($total/$div_base))" "$div_name" "$1"
	}

	shift
done


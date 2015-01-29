#!/bin/sh

if [ "$1" ]; then
	since="$1"
else
	since="`date "+%Y-%m-%d"`"
fi

if [ "$2" ]; then
	until="$2"
else
	until="now"
fi

journalctl _SYSTEMD_UNIT=sshd.service \
	--since="$since" --until="$until" | \
	grep 'Failed password for' | \
	sed -e 's/.*from\ //g' -e 's/\ port.*//g' | sort -n | {
		count=0;
		firstrun=0;
		printed=0;
		while read oneline;
		do
			printed=0;
			if [ "$prevline" != "$oneline" ] && [ "$firstrun" = "1" ];
			then
				echo "$count $prevline";
				count=0;
				printed=1;
			fi
			count=$(($count+1));
			prevline="$oneline";
			firstrun=1;
		done
		if [ "$printed" = "0" ];
		then
			echo "$count $prevline";
		fi } | \
	sort -nr

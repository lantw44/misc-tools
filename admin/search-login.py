#!/usr/bin/env python3

import sys
import re
from datetime import datetime

if len(sys.argv) < 3:
    sys.stderr.write(
        'Usage: {} output_of_last_FRw event_list\n'.format(sys.argv[0]))
    quit(1)

last_output = open(sys.argv[1], 'r')
event_list = open(sys.argv[2], 'r')
records = []

while True:
    last_line_raw = last_output.readline().strip()
    if not last_line_raw:
        break

    last_line = last_line_raw
    user_end_index = last_line.find(' ')
    user = last_line[0:user_end_index]
    if user == 'reboot':
        continue

    last_line = last_line[user_end_index:len(last_line)].strip()
    terminal_end_index = last_line.find(' ')
    terminal = last_line[0:terminal_end_index]

    day_start_index = last_line.find(' ')
    last_line = last_line[day_start_index:len(last_line)].strip()
    date_start_index = last_line.find(' ')
    last_line = last_line[date_start_index:len(last_line)].strip()

    login_time = last_line[0:20]
    separator = last_line[20:23]
    logout_time = last_line[27:47]

    login = datetime.strptime(login_time, '%b %d %H:%M:%S %Y')
    if separator == ' - ' and not logout_time.startswith('    '):
        logout = datetime.strptime(logout_time, '%b %d %H:%M:%S %Y')
    else:
        logout = datetime.max

    records.append({
        'user': user,
        'tty': terminal,
        'login': login,
        'logout': logout,
        'raw': last_line_raw
    })


while True:
    event_raw = event_list.readline().strip()
    if not event_raw:
        break

    event = event_raw
    event_time = datetime.strptime(event, '%Y-%m-%d %H:%M:%S')

    for record in records:
        if event_time >= record['login'] and event_time <= record['logout']:
            print(event_time, '{0:16} => {1}'.format(record['user'], record['raw']))

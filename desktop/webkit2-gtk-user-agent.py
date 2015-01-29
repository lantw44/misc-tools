#!/usr/bin/env python

from gi.repository import WebKit2

version = '{}.{}.{}'.format(
	WebKit2.get_major_version(),
	WebKit2.get_minor_version(),
	WebKit2.get_micro_version())
user_agent = WebKit2.WebView().get_settings().get_user_agent()

print('version = {}, user-agent = {}'.format(version, user_agent))

#!/usr/bin/env python

from gi.repository import WebKit

version = '{}.{}.{}'.format(
	WebKit.major_version(),
	WebKit.minor_version(),
	WebKit.micro_version())
user_agent = WebKit.WebView().get_settings().get_user_agent()

print('version = {}, user-agent = {}'.format(version, user_agent))

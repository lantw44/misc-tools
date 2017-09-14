#!/usr/bin/env python3

flickr_api_key = 'e65a9f9957d8f6ae7490072452c0a345'
flickr_group_id = '<Insert your flickr group ID here>'

def flickr_url(page):
	return '{}?api_key={}&method={}&group_id={}&extras={}&page={}&per_page={}'.format(
		'https://api.flickr.com/services/rest/',
		flickr_api_key, 'flickr.photos.search',
		flickr_group_id, 'url_o', page, 500)


import os
import urllib.request
from xml.etree import ElementTree

def flickr_request(page):
	url = flickr_url(page)
	print('Retrieving information from page {} ...'.format(page), end='', flush=True)
	info = urllib.request.urlopen(url)
	print(' done')
	return info.read()

def flickr_download(url):
	fname = os.path.basename(urllib.parse.urlsplit(url).path)
	try:
		f = open(fname, 'xb')
	except FileExistsError:
		print('Skipping {}'.format(url))
		return

	print('Downloading {} ...'.format(url), end='', flush=True)
	data = urllib.request.urlopen(url).read()
	print(' done')
	f.write(data)
	f.close()

info = ElementTree.fromstring(flickr_request(1))
pages = int(info.find('photos').get('pages'))
photos = int(info.find('photos').get('total'))
print('There are {} photos ({} pages)'.format(photos, pages))

count = 0
for page in range(1, pages + 1):
	info = ElementTree.fromstring(flickr_request(page))
	for node in info.iter():
		if node.tag == 'photo':
			count = count + 1
			print('[{}/{}] '.format(count, photos), end='', flush=True)
			url = node.get('url_o')
			flickr_download(url)

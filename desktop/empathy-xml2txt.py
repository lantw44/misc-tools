#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys
from lxml import etree

def empathy_xml2txt(infile, outfile):
	xmlparser = etree.XMLParser(encoding = 'UTF-8')
	xmltree = etree.parse(infile, xmlparser)
	xmlroot = xmltree.getroot()
	for msg in xmlroot.iter():
		if msg.tag == "message":
			outfile.write("{} <{:^12}> {}\n".format(
				msg.get('time').replace('T', ' '),
				msg.get('id'),
				msg.text.encode('UTF-8')))

if __name__ == "__main__":
	for i in sys.argv[1:]:
		empathy_xml2txt(i, sys.stdout)

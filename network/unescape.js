#!/usr/bin/env seed

const Gio = imports.gi.Gio;

var path = '/dev/stdin';
if (Seed.argv.length >= 3) {
	path = Seed.argv[2];
}

var file = Gio.file_new_for_path(path);
var istream = new Gio.DataInputStream.c_new(file.read());

var line;
while ((line = istream.read_line_utf8()) != undefined) {
	print(unescape(line.replace(/\+/g, ' ')));
}

istream.close();

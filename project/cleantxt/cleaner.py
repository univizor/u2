# -*- coding: utf-8 -*-
import hashlib
import collections
import re
import cld2
from re import sub


def remove_repeated_lines(content):
	d = collections.defaultdict(int)
	content_lines = content.split("\n")

	output_lines = []
	removed_lines = []

	for l in content_lines:
		d[l] += 1

	for l in content_lines:
		if d[l] < 10:
			output_lines.append(l)
	else:
		removed_lines.append(l)

	return ("\n".join(output_lines), removed_lines)


def clean_ng(text):
	"""Next generation of cleaning. Use this!"""

	# Funky new-lines
	text = text.replace("", " ")
	text = text.replace("\t\n", "\n")

	# White space
#	text = sub("\n", " ", text)
#	text = sub("\s+", " ", text)

	# Exceptions and aliases
	text = text.replace(" npr. ", " na primer ")
	text = text.replace(" ozr. ", " oziroma ")
	text = text.replace(" itd. ", " in tako dalje ")
	text = sub("Dipl.\sdelo", "Diplomsko delo", text)
	text = sub("dipl.\sdelo", "diplomsko delo", text)
	text = sub("Univ.\sv", "Univerza v", text)
	text = sub("Univ.\sV", "Univerza V", text)

	# Everything except this
#	text = sub(u"[^a-zA-Z0-9šđčćžŠĐČĆŽ\n\ \.\!\;\,\?\-\+]", "", text)

	# Again remove white-space
#	text = sub("\s+", " ", text)
	return [text.strip(), None]

def remove_before(s, content, removed):
	matches = re.finditer(s, content, re.IGNORECASE)
	if not matches:
		return content
	last_ok_match = None
	for match in matches:
		if not match:
			continue
		if match.start() > 0 and match.start()<len(content)/2:
			last_ok_match = match 
	if not last_ok_match:
		return content
	pos = last_ok_match.start()
	removed = ""

	if pos > 0 and pos < len(content)/2:
		removed += content[0:last_ok_match.end()]
		content = content[last_ok_match.end():]
	return content

def remove_after(s, content, removed):
	match = re.search(s, content, re.IGNORECASE)

	if not match:
		return content

	pos = match.start()
	removed = ""

	if pos > 0 and pos > len(content)/2:
		content = content[0:pos]
		removed += content[pos:]
	return content

def remove_intro(content):
	removed = ""
	content = remove_before("\n(?:[\d\s\.]*)uvod\n", content, removed)
	content = remove_before("\n(?:[\d\s\.]*)introduction\n", content, removed)
	content = remove_before("\n(?:[\d\s\.]*)1 introduction\n", content, removed)
	content = remove_before("\n(?:[\d\s\.]*)uvod\n", content, removed)
	content = remove_before("\n(?:[\d\s\.]*)povzetek\n", content, removed)
	content = remove_before("\n(?:[\d\s\.xiv]*)references\n", content, removed)
	return [content, removed]

def remove_lit(content):
	removed = ""
	content = remove_after("\n(?:[\d\s\.]*)literatura\n", content, removed)
	content = remove_after("\n(?:[\d\s\.]*)viri\n", content, removed)
	content = remove_after("\n(?:[\d\s\.]*)references\n", content, removed)
	content = remove_after("\n(?:[\d\s\.]*)literatura in viri\n", content, removed)
	return [content, None]

def replace(content, rep):
	rep = dict((re.escape(k), v) for k, v in rep.iteritems())
	pattern = re.compile("|".join(rep.keys()))
	content = pattern.sub(lambda m: rep[re.escape(m.group(0))], content)
	return content
	
def fix_sumniki(content):
	# from http://stackoverflow.com/questions/6116978/python-replace-multiple-strings
	rep = {
		#5067
		"\xc2\x83": "Č",
		"\xc2\x92": "Š",
		"\xc2\x9a": "Ž",
		"\xc2\xa3": "č",
		"\xc2\xb2": "š",
		"\xc2\xba": "ž",
		"": "fi",	# 0x1c
		"": "\"",	# 0x10
		"": "\"",	# 0x11
		# 6424
		"ˇc": "č",
		"ˇs": "š",
		"ˇz": "ž",
		"ˇ\nc": "č",
		"ˇ\ns": "š",
		"ˇ\nz": "ž",
		"•": "",
		"●": "",
		# 1
		"ĉ": "č",
		"Ĉ": "Č",
		"ţ": "ž",
		# empty chars:
		" ": "",
	}
	return [replace(content, rep), None]


def lower(content):
	rep = {
		"Ć": "ć",
		"Đ": "đ",
		"Č": "č",
		"Š": "š",
		"Ž": "ž",
	}
	content = replace(content.lower(), rep)
	return [content, None]

def get_cleaned(content):
	[content, removed] = fix_sumniki(content)
	[content, removed] = lower(content)
	[content, removed] = clean_ng(content)
#	print content[:200]
#	print "XXXXXXXX"
	[content, removed] = remove_repeated_lines(content)
	[content, removed] = remove_intro(content)
	[content, removed] = remove_lit(content)	
	return content
			


def is_slovene(content):
	a, b, languages = cld2.detect(content)
	return 'SLOVENIAN' in [x[0] for x in languages]


def get_hash(content):
	m = hashlib.md5()
	m.update(content)
	return m.hexdigest()






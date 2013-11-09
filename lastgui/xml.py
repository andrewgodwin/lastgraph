"""
Last.fm XML parser
"""

import sys

from BeautifulSoup import BeautifulStoneSoup
import htmllib

def unescape(s):
	p = htmllib.HTMLParser(None)
	p.save_bgn()
	p.feed(s)
	return p.save_end()


def week_list(xml):
	
	soup = BeautifulStoneSoup(xml)
	
	# Check this is the right thing
	assert soup.find("weeklychartlist"), "week_list did not get a Weekly Chart List"
	
	for tag in soup.findAll("chart"):
		yield int(tag['from']), int(tag['to'])


def weekly_artists(xml):
	soup = BeautifulStoneSoup(xml)
	
	# Check this is the right thing
	try:
		assert soup.find("weeklyartistchart"), "weekly_artists did not get a Weekly Artist Chart"
	except AssertionError:
		print >> sys.stderr, xml
		raise AssertionError("weekly_artists did not get a Weekly Artist Chart")
	
	# Get the artists
	for tag in soup.findAll("artist"):
		name = str(tag.find("name").string).decode("utf8")
		playtag = tag.find("playcount")
		if playtag:
			plays = long(playtag.string)
		else:
			plays = float(tag.find("weight").string)
		yield unescape(name), plays
	

"""
Last.fm data fetcher
"""

import sys
import time
import socket
import urllib
import random
import eventlet
from lastgui.xml import *
from lastgui.storage import UserHistory
from django.conf import settings

class LastFmFetcher(object):
    
    def __init__(self):
        self.last = 0.0
        self.delay = 1.0
        self.debug = True
    
    
    def fetch(self, url):
        import time
        # Delay to ensure we don't anger the API server
        while self.last + self.delay > time.time():
            time.sleep(0.001)
        # Nab
        if self.debug:
            print "Fetching %s" % url
        else:
            pass #print >> sys.stderr, "Fetching %s" % url
        
        
        try:
            socket.settimeout(10)
            handle = urllib.urlopen(url)
            data = handle.read()
            #print >> sys.stderr, dict(handle.headers), "for", url
        except (AttributeError, IOError):
            try:
                time.sleep(0.1)
                data = urllib.urlopen(url).read()
            except (AttributeError, IOError):
                try:
                    time.sleep(0.2+random.random()*0.2)
                    data = urllib.urlopen(url).read()
                except (AttributeError, IOError):
                    try:
                        time.sleep(0.3)
                        data = urllib.urlopen(url).read()
                    except (AttributeError, IOError):
                        try:
                            time.sleep(0.4)
                            data = urllib.urlopen(url).read()
                        except (AttributeError, IOError):
                            raise IOError("Cannot contact last.fm")
        
        self.last = time.time()
        return data
    
    
    def weeks(self, username):
        if username.startswith("tag:"):
            return week_list(
                self.fetch("http://ws.audioscrobbler.com/2.0/?method=tag.getweeklychartlist&tag=%s&api_key=%s" % (username[4:], settings.API_KEY))
            )
        elif username.startswith("group:"):
            return week_list(
                self.fetch("http://ws.audioscrobbler.com/2.0/?method=group.getweeklychartlist&group=%s&api_key=%s" % (username[6:], settings.API_KEY))
            )
        else:
            return week_list(
                self.fetch("http://ws.audioscrobbler.com/2.0/?method=user.getweeklychartlist&user=%s&api_key=%s" % (username, settings.API_KEY))
            )
    
    
    def weekly_artists(self, username, start, end):
        if username.startswith("tag:"):
            return weekly_artists(
                self.fetch("http://ws.audioscrobbler.com/2.0/?method=tag.getweeklyartistchart&tag=%s&api_key=%s&from=%s&to=%s" % (username[4:], settings.API_KEY, start, end))
            )
        elif username.startswith("group:"):
            return weekly_artists(
                self.fetch("http://ws.audioscrobbler.com/2.0/?method=group.getweeklyartistchart&group=%s&api_key=%s&from=%s&to=%s" % (username[6:], settings.API_KEY, start, end))
            )
        else:
            return weekly_artists(
                self.fetch("http://ws.audioscrobbler.com/2.0/?method=user.getweeklyartistchart&user=%s&api_key=%s&from=%s&to=%s" % (username, settings.API_KEY, start, end))
            )


fetcher = LastFmFetcher()


def update_user_history(uh):
    """Given a UserHistory object, updates it so it is current."""
    
    fetcher.delay = settings.LASTFM_DELAY
    
    for start, end in fetcher.weeks(uh.username):
        if not uh.has_week(start):
            try:
                for artist, plays in fetcher.weekly_artists(uh.username, start, end):
                    uh.set_plays(artist, start, plays)
            except:
                # Try once more
                try:
                    for artist, plays in fetcher.weekly_artists(uh.username, start, end):
                        uh.set_plays(artist, start, plays)
                except KeyboardInterrupt:
                    print "Exiting on user command."
                    raise SystemExit
                except Exception, e:
                    print "Warning: Invalid data for %s - %s: %s" % (start, end, repr(e))


def update_user(username):
    """Returns an up-to-date UserHistory for this username,
    perhaps creating it on the way or loading from disk."""
    
    uh = UserHistory(username)
    
    if uh.has_file():
        uh.load_default()
    
    try:
        update_user_history(uh)
        uh.set_timestamp() # We assume we got all the data for now.
    except KeyboardInterrupt:
        pass
    
    uh.save_default()
    
    return uh

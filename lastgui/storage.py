"""
LastGraph data storage stuff.
"""

import os
import time

# Get a pickle - the faster the better
try:
    import cPickle as pickle
except ImportError:
    print "Warning: Cannot find cPickle."
    import pickle


class UserHistory(object):
    
    """
    Represents a user's listening history, with artist-week-level granularity.
    """
    
    def __init__(self, username):
        self.username = username
        self.artists = {}
        self.weeks = {}
        self.timestamp = 0
    
    def set_plays(self, artist, week, plays):
        "Set the number of plays for an artist on a week."
        if artist not in self.artists:
            self.artists[artist] = {}
        self.artists[artist][week] = plays
        if week not in self.weeks:
            self.weeks[week] = {}
        self.weeks[week][artist] = plays
    
    def delete_week(self, week):
        "Erases all plays for a week"
        if week in self.weeks:
            del self.weeks[week]
            for artist in self.artists:
                if week in self.artists[artist]:
                    del self.artists[artist][week]
    
    def get_plays(self, artist, week):
        "Gets the number of plays for an artist in a week."
        return self.artists.get(artist, {}).get(week, 0)
    
    def total_artist(self, artist):
        return sum(self.artists.get(artist, {}).values())
    
    def total_week(self, week):
        return sum(self.weeks.get(week, {}).values())
    
    def artist_plays(self, artist):
        plays = {}
        for week in self.weeks:
            plays[week] = self.artists.get(artist, {}).get(week, 0)
        return plays
    
    def week_plays(self):
        plays = {}
        for week, artists in self.weeks.items():
            plays[week] = sum(artists.values())
        return plays
    
    def has_week(self, week):
        return week in self.weeks
    
    def num_weeks(self):
        return len(self.weeks)
    
    def num_artists(self):
        return len(self.artists)
    
    def save(self, file):
        #print "Saving %s..." % self.username
        pickle.dump((self.username, self.timestamp, self.artists, self.weeks), file, -1)
    
    def save_default(self):
        self.save(open(self.get_default_path(), "w"))
    
    def load(self, file):
        try:
            self.username, self.timestamp, self.artists, self.weeks = pickle.load(file)
        except EOFError:
            raise ValueError("Invalid pickle file '%s'" % file)
        #print "Loading %s..." % self.username
    
    def load_default(self):
        self.load(open(self.get_default_path(), "r"))
    
    def has_file(self):
        return os.path.isfile(self.get_default_path())
    
    def set_timestamp(self, ttime=None):
        if ttime is None:
            ttime = time.time()
        self.timestamp = ttime
    
    def data_age(self):
        return time.time() - self.timestamp
    
    def get_default_path(self):
        from django.conf import settings
        return os.path.join(settings.USER_DATA_ROOT, "%s.last" % self.username)
    
    def load_if_possible(self):
        if self.has_file():
            try:
                self.load_default()
            except ValueError:
                pass




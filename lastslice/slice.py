#!/usr/bin/python
import os
import sys
import web
import time
import random
import datetime
import threading
from StringIO import StringIO

FILEROOT = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(FILEROOT, ".."))
sys.path.insert(1, os.path.join(FILEROOT, "..", "lib"))

os.environ['DJANGO_SETTINGS_MODULE'] = "settings"

from colorsys import *

from graphication import *
from graphication.wavegraph import WaveGraph
from graphication.color import hex_to_rgba

from PIL import Image

import lastslice.shortslice_css as slice_style
import lastslice.longslice_css as long_style

from lastgui.fetch import fetcher

from django.core.cache import cache


errfile = open("/tmp/sliceerr.txt", "a")

urls = (
    "/slice/([^/]+)/", "Slice",
    "/slice/([^/]+)/(\d+)/(\d+)/", "Slice",
    "/slice/([^/]+)/(\d+)/(\d+)/([^/]+)/", "Slice",
    "/longslice/([^/]+)/", "LongSlice",
    "/longslice/([^/]+)/.pdf", "LongSlicePDF",
    "/longslice/([^/]+)/(\d+)/(\d+)/", "LongSlice",
    "/longslice/([^/]+)/(\d+)/(\d+)/([^/]+)/", "LongSlice",
    "/colours/([^/]+)/", "Colours",
)
fetcher.debug = False

class DataError(StandardError): pass


def rgba_to_hex(r, g, b, a):
    return "%02x%02x%02x%02x" % (r*255,g*255,b*255,a*255)


class ThreadedWeek(threading.Thread):
    
    def __init__(self, user, start, end):
        threading.Thread.__init__(self)
        self.user = user
        self.range = start, end
    
    def run(self):
        self.data = list(fetcher.weekly_artists(self.user, self.range[0], self.range[1]))


def get_data(user, length=4):
    
    cache_key = 'user_%s:%s' % (length, user.replace(" ","+"))
    
    data = None #cache.get(cache_key)
    while data == "locked":
        time.sleep(0.01)
    
    if not data:
        
        #cache.set(cache_key, "locked", 5)
        try:
            weeks = list(fetcher.weeks(user))
        except:
            import traceback
            try:
                errfile.write(traceback.format_exc())
                errfile.flush()
            except:
                pass
            return None, None
        threads = [ThreadedWeek(user, start, end) for start, end in weeks[-length:]]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        data = ([thread.data for thread in threads], weeks[-length:])
    
    #cache.set(cache_key, data, 30)
    
    return data


def get_series(user, length=4, limit=15):

    if ":" in user:
        user = user.replace("_", "+")
        
    data, weeks = get_data(user, length)

    if not data and not weeks:
        data, weeks = get_data(user, length)
        if not data and not weeks:
            data, weeks = get_data(user, length)
            if not data and not weeks:
                return None
    
    artists = {}
        
    for week in data:
        for artist, plays in week:
            artists[artist] = []
    
    for week in data:
        week = dict(week)
        for artist in artists:
            plays = week.get(artist, 0)
            if plays < 2:
                plays = 0
            artists[artist].append(plays)
    
    artists = artists.items()
    artists.sort(key=lambda (x,y):max(y))
    artists.reverse()
    
    sh, ss, sv = rgb_to_hsv(*hex_to_rgba("ec2d60")[:3])
    eh, es, ev = rgb_to_hsv(*hex_to_rgba("0c4da2")[:3])
    a = True
    ad = 0.3
    
    th, ts, tv = (eh-sh)/float(limit), (es-ss)/float(limit), (ev-sv)/float(limit)
    
    series_set = SeriesSet()
    for artist, data in artists[:15]:
        series_set.add_series(Series(
            artist,
            dict([(datetime.datetime.fromtimestamp(weeks[i][0]), x) for i, x in enumerate(data)]),
            rgba_to_hex(*(hsv_to_rgb(sh, ss, sv) + (a and 1 or 1-ad,))),
        ))
        sh += th
        ss += ts
        sv += tv
        a = not a
        ad += (0.6/limit)
    
    return series_set


class Slice(object):
    
    def GET(self, username, width=230, height=138, labels=False):
        web.header("Content-Type", "image/png")
        
        width = int(width)
        height = int(height)
        
        series_set = get_series(username)
        output = FileOutput(padding=0, style=slice_style)
        
        if series_set:
            # Create the output
            scale = AutoWeekDateScale(series_set, short_labels=True)
        
            # OK, render that.
            wg = WaveGraph(series_set, scale, slice_style, bool(labels), vertical_scale=False)
            output.add_item(wg, x=0, y=0, width=width, height=height)
        else:
            output.add_item(Label("invalid username"), x=0, y=0, width=width, height=height)

        print output.stream('png').read()


class LongSlice(object):
    
    def GET(self, username, width=1200, height=400, labels=False):
        web.header("Content-Type", "image/png")
        
        width = int(width)
        height = int(height)
        
        series_set = get_series(username, 12, 25)
        
        # Create the output
        output = FileOutput(padding=0, style=long_style)
        
        if series_set:
            scale = AutoWeekDateScale(series_set, year_once=False)
        
            # OK, render that.
            wg = WaveGraph(series_set, scale, long_style, not bool(labels), textfix=True)
            output.add_item(wg, x=0, y=0, width=width, height=height)
        else:
            output.add_item(Label("invalid username"), x=0, y=0, width=width, height=height)


        
        # Load it into a PIL image
        img = Image.open(output.stream('png'))
        
        # Load the watermark
        mark = Image.open(os.path.join(os.path.dirname(__file__), "watermark.png"))
        
        # Combine them
        nw, nh = img.size
        nh += 40
        out = Image.new("RGB", (nw, nh), "White")
        out.paste(img, (0,0))
        out.paste(mark, (width-210, height+10))
        
        # Stream the result
        outf = StringIO()
        out.save(outf, "png")
        outf.seek(0)
        print outf.read()



class LongSlicePDF(object):
    
    def GET(self, username, width=1200, height=400, labels=False):
        web.header("Content-Type", "application/x-pdf")
        
        width = int(width)
        height = int(height)
        
        series_set = get_series(username, 12, 25)
        
        # Create the output
        output = FileOutput(padding=0, style=long_style)
        scale = AutoWeekDateScale(series_set)
        
        # OK, render that.
        wg = WaveGraph(series_set, scale, long_style, not bool(labels), textfix=True)
        output.add_item(wg, x=0, y=0, width=width, height=height)
        print output.stream('pdf').read()


class Colours:
    
     def GET(self, username):
        
        series_set = get_series(username)
        
        for series in series_set:
            print "%s,%s" % (series.title, series.color)


#web.webapi.internalerror = web.debugerror
if __name__ == "__main__": web.run(urls, globals())

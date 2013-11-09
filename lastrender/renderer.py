#!/usr/bin/python

"""
LastGraph rendering client
"""

import sys
import os
import json
import urllib
from httppost import posturl, extract_django_error
from graphication import FileOutput, Series, SeriesSet, Label, AutoWeekDateScale, Colourer, css
from graphication.wavegraph import WaveGraph


def render_poster():
    from settings import apiurl, local_store, local_store_url, nodename, nodepwd

    DEBUG = "--debug" in sys.argv
    GDEBUG = "--gdebug" in sys.argv
    TEST = "--test" in sys.argv
    PROXYUPLOAD = "--proxyupload" in sys.argv

    if "--" not in sys.argv[-1] and TEST:
        SPECIFIC = int(sys.argv[-1])
    else:
        SPECIFIC = None

    print "# Welcome to the LastGraph Renderer"

    print "# This is node '%s'." % nodename
    print "# Using server '%s'." % apiurl

    def jsonfetch(url):
        """Fetches the given URL and parses it as JSON, then returns the result."""
        try:
            data = urllib.urlopen(url).read()
        except AttributeError:
            sys.exit(2001)
        if data[0] == "(" and data[-1] == ")":
            data = data[1:-1]
        try:
            return json.loads(data)
        except ValueError:
            if DEBUG:
                print extract_django_error(data)
            raise ValueError

    # See if we need to download something to render
    try:
        if SPECIFIC:
            print "~ Rendering only graph %s." % SPECIFIC
            status = jsonfetch(apiurl % "render/data/%i/?nodename=%s&password=%s" % (SPECIFIC, nodename, nodepwd))
        else:
            status = jsonfetch(apiurl % "render/next/?nodename=%s&password=%s" % (nodename, nodepwd))

    except ValueError:
        print "! Garbled server response to 'next render' query."
        sys.exit(0)

    except IOError:
        print "! Connection error to server"
        sys.exit(0)

    if "error" in status:
        print "! Error from server: '%s'" % status['error']
        sys.exit(0)

    elif "id" in status:

        try:
            id = status['id']
            username = status['username']
            start = status['start']
            end = status['end']
            data = status['data']
            params = status['params']
            colourscheme, detail = params.split("|")
            detail = int(detail)

            print "* Rendering graph #%s for '%s' (%.1f weeks)" % (id, username, (end-start)/(86400.0*7.0))

            # Gather a list of all artists
            artists = {}
            for week_start, week_end, plays in data:
                for artist, play in plays:
                    try:
                        artist.encode("utf-8")
                        artists[artist] = {}
                    except (UnicodeDecodeError, UnicodeEncodeError):
                        print "Bad artist!"

            # Now, get that into a set of series
            for week_start, week_end, plays in data:
                plays = dict(plays)
                for artist in artists:
                    aplays = plays.get(artist, 0)
                    if aplays < detail:
                        aplays = 0
                    artists[artist][week_end] = aplays

            series_set = SeriesSet()
            for artist, plays in artists.items():
                series_set.add_series(Series(artist, plays))

            # Create the output
            output = FileOutput()

            import lastgraph_css as style

            # We'll have major lines every integer, and minor ones every half
            scale = AutoWeekDateScale(series_set)

            # Choose an appropriate colourscheme
            c1, c2 = {
                "ocean": ("#334489", "#2d8f3c"),
                "blue": ("#264277", "#338a8c"),
                "desert": ("#ee6800", "#fce28d"),
                "rainbow": ("#ff3333", "#334489"),
                "sunset": ("#aa0000", "#ff8800"),
                "green": ("#44ff00", "#264277"),
                "eclectic": ("#510F7A", "#FFc308"),
            }[colourscheme]

            style = style.merge(css.CssStylesheet.from_css("colourer { gradient-start: %s; gradient-end: %s; }" % (c1, c2)))

            # Colour that set!
            cr = Colourer(style)
            cr.colour(series_set)

            # OK, render that.
            wg = WaveGraph(series_set, scale, style, debug=GDEBUG, textfix=True)
            lb = Label(username, style)

            width = 30 * len(series_set.keys())
            output.add_item(lb, x=10, y=10, width=width-20, height=20)
            output.add_item(wg, x=0, y=40, width=width, height=300)

            # Save the images

            if TEST:
                output.write("pdf", "test.pdf")
                print "< Wrote output to test.pdf"
            else:
                pdf_stream = output.stream("pdf")
                print "* Rendered PDF"
                svgz_stream = output.stream("svgz")
                print "* Rendered SVG"
                urls = {}
                for format in ('svgz', 'pdf'):
                    filename = 'graph_%s.%s' % (id, format)
                    fileh = open(os.path.join(local_store, filename), "w")
                    fileh.write({'svgz': svgz_stream, 'pdf': pdf_stream}[format].read())
                    fileh.close()
                    urls[format] = "%s/%s" % (local_store_url.rstrip("/"), filename)

                print "< Successful. Telling server..."
                response = posturl(apiurl % "render/links/", [
                    ("nodename", nodename), ("password", nodepwd), ("id", id),
                    ("pdf_url", urls['pdf']), ("svg_url", urls['svgz']),
                ], [])
                if DEBUG:
                    print extract_django_error(response)
                print "* Done."
                if "pdf_stream" in locals():
                    pdf_stream.close()
                if "svgz_stream" in locals():
                    svgz_stream.close()

        except:
            import traceback
            traceback.print_exc()
            print "< Telling server about error..."
            if "pdf_stream" in locals():
                pdf_stream.close()
            if "svgz_stream" in locals():
                svgz_stream.close()
            try:
                jsonfetch(apiurl % "render/failed/?nodename=%s&password=%s&id=%s" % (nodename, nodepwd, id))
                response = posturl(apiurl % "render/failed/", [
                    ("nodename", nodename), ("password", nodepwd), ("id", id),
                    ("traceback", traceback.format_exc()),
                ], [])
                print "~ Done."
            except:
                print "! Server notification failed"
            sys.exit(0)

    elif "nothing" in status:
        if "skipped" in status:
            print "~ Server had to skip: %s." % status['skipped']
        else:
            print "- No graphs to render."

    if SPECIFIC:
        sys.exit(0)


if __name__ == "__main__":
    render_poster()

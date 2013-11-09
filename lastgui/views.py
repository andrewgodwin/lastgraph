
import datetime
from urlparse import urlparse

from shortcuts import *

from lastgui.models import *
from lastgui.storage import UserHistory
from lastgui.fetch import fetcher
from lastgui.data import hotlink_png

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django import forms

from lastgui.export import as_filetype


def user_ready(username):
    if username.endswith(".php"):
        return False
    
    uh = UserHistory(username)
    
    # First, check to see if the file is fresh
    uh.load_if_possible()
    if uh.data_age() < settings.HISTORY_TTL:
        return uh.num_weeks()
    
    # Then, do a quick weeklist fetch to compare
    try:
        weeks = list(fetcher.weeks(username))
    except AssertionError:  # They probably don't exist
        return None
    
    present = True
    for start, end in weeks:
        if not uh.has_week(start):
            present = False
            break
    
    # If all weeks were present, update the timestamp
    if present:
        uh.set_timestamp()
        uh.save_default()
        return len(weeks)
    else:
        return False


def referrer_limit(ofunc):
    def nfunc(request, username, *a, **kw):
        referrer = request.META.get('HTTP_REFERER', None)
        if referrer:
            protocol, host, path, params, query, frag = urlparse(referrer)
            if host != request.META['HTTP_HOST']:
                user = LastFmUser.by_username(username)
                if not user.external_allowed():
                    return HttpResponse(hotlink_png, mimetype="image/png")
        return ofunc(request, username, *a, **kw)
    return nfunc


def ready_or_update(username):
    
    ready = user_ready(username)
    if ready is False:  # We need to update their data
        lfuser = LastFmUser.by_username(username)
        if not lfuser.requested_update:
            lfuser.requested_update = datetime.datetime.utcnow()
            lfuser.last_check = datetime.datetime.utcnow()
            lfuser.save()
    
    return ready


def ajax_user_ready(request, username):
    "Returns if the given user's data is in the system ready for lastgraph."
    
    ready = ready_or_update(username)
    
    return jsonify(ready)


def ajax_user_queuepos(request, username):
    "Returns what number the user is in the request queue."
    
    try:
        return jsonify(list(LastFmUser.queue()).index(LastFmUser.by_username(username)) + 1)
    except (ValueError, IndexError):
        return jsonify(None)


### Graphs ###

from graphication import FileOutput, Series, SeriesSet, AutoWeekDateScale, Label
from graphication.wavegraph import WaveGraph
from lastgui.css import artist_detail_css, artist_detail_white_css, basic_timeline_css, sig1_css


def stream_graph(output):
    response = HttpResponse(mimetype="image/png")
    response.write(output.stream("png").read())
    return response


@referrer_limit
@cache_page(60 * 15)
def graph_artist(request, username, artist, width=800, height=300):
    
    ready_or_update(username)
    
    width = int(width)
    height = int(height)
    
    if not width:
        width=800
    
    if not height:
        width=300
    
    uh = UserHistory(username)
    uh.load_if_possible()
    
    series_set = SeriesSet()
    series_set.add_series(Series(
        artist,
        uh.artist_plays(artist),
        "#369f",
        {0:4},
    ))
    
    # Create the output
    output = FileOutput(padding=0, style=artist_detail_white_css)
    
    try:
        scale = AutoWeekDateScale(series_set, short_labels=True, month_gap=2)
    except ValueError:
        raise Http404("Bad data (ValueError)")
    
    # OK, render that.
    wg = WaveGraph(series_set, scale, artist_detail_white_css, False, vertical_scale=True)
    output.add_item(wg, x=0, y=0, width=width, height=height)
    
    # Save the images
    return stream_graph(output)


def graph_timeline_data(username):
    
    uh = UserHistory(username)
    uh.load_if_possible()
    
    series_set = SeriesSet()
    series_set.add_series(Series(
        "Plays",
        uh.week_plays(),
        "#369f",
        {0:4},
    ))
    
    return series_set


@referrer_limit
@cache_page(60 * 15)
def graph_timeline(request, username, width=800, height=300):
    
    ready_or_update(username)
    
    width = int(width)
    height = int(height)
    
    if not width:
        width = 800
    
    if not height:
        height = 300
    
    series_set = graph_timeline_data(username)
    
    # Create the output
    output = FileOutput(padding=0, style=artist_detail_white_css)
    try:
        scale = AutoWeekDateScale(series_set, short_labels=True, month_gap=2)
    except ValueError:
        raise Http404("No data")
    
    # OK, render that.
    wg = WaveGraph(series_set, scale, artist_detail_white_css, False, vertical_scale=True)
    output.add_item(wg, x=0, y=0, width=width, height=height)
    
    # Save the images
    try:
        return stream_graph(output)
    except ValueError:
        raise Http404("No data")


@referrer_limit
@cache_page(60 * 15)
def graph_timeline_basic(request, username, width=800, height=300):
    
    ready_or_update(username)
    
    width = int(width)
    height = int(height)
    
    if not width:
        width = 1280
    
    if not height:
        height = 50
    
    series_set = graph_timeline_data(username)
    series_set.get_series(0).color = "3695"
    
    # Create the output
    output = FileOutput(padding=0, style=basic_timeline_css)
    try:
        scale = AutoWeekDateScale(series_set, short_labels=True)
    except ValueError:
        raise Http404("No data")
    
    # OK, render that.
    wg = WaveGraph(series_set, scale, basic_timeline_css, False, vertical_scale=False)
    output.add_item(wg, x=0, y=0, width=width, height=height)
    
    # Save the images
    try:
        return stream_graph(output)
    except ValueError:
        raise Http404("No data")



@referrer_limit
@cache_page(60 * 15)
def graph_sig1(request, username, width=300, height=100):
    
    ready_or_update(username)
    
    width = int(width)
    height = int(height)
    
    if not width:
        width = 300
    
    if not height:
        height = 100
    
    series_set = graph_timeline_data(username)
    series_set.get_series(0).color = "3695"
    
    # Create the output
    output = FileOutput(padding=0, style=sig1_css)
    try:
        scale = AutoWeekDateScale(series_set, short_labels=True)
    except ValueError:
        raise Http404("No data")
    
    # OK, render that.
    
    lb = Label(username, sig1_css)
    output.add_item(lb, x=10, y=20-(height/2), width=width, height=height)
    wg = WaveGraph(series_set, scale, sig1_css, False, vertical_scale=False)
    output.add_item(wg, x=0, y=0, width=width, height=height)
    
    # Save the images
    try:
        return stream_graph(output)
    except ValueError:
        raise Http404("No data")



def front(request):
    
    return render(request, "front.html", {
        "recent": LastFmUser.objects.filter(requested_update__isnull=True).order_by("-last_check")[:5],
    })


def status(request):
    
    return render(request, "status.html", {
        "fetchqueue": LastFmUser.queue(),
        "renderqueue": Poster.queue(),
        "numprofiles": LastFmUser.objects.count(),
        "numposters": Poster.objects.count(),
        "recentposters": Poster.objects.filter(completed__isnull=False).order_by("-completed")[:10],
        "nodes": Node.recent(),
    })


def status_nagios_fetch(request):
    
    return HttpResponse(str(LastFmUser.queue().count()))


def status_nagios_render(request):
    
    return HttpResponse(str(Poster.queue().count()))



def user_root(request, username):
    
    ready = ready_or_update(username)
    if not ready:
        flash(request, "This user's data is currently out-of-date, and is being updated.")
    
    uh = UserHistory(username)
    uh.load_if_possible()
    
    lfuser = LastFmUser.by_username(username)
    
    return render(request, "user_root.html", {"username": username, "num_weeks": len(uh.weeks), "lfuser": lfuser})




def user_sigs(request, username):
    
    lfuser = LastFmUser.by_username(username)
    
    if not lfuser.external_allowed():
        raise Http404("No premium account")
    
    return render(request, "user_sigs.html", {"username": username, "lfuser": lfuser})




def user_artists(request, username):
    
    uh = UserHistory(username)
    uh.load_if_possible()
    
    artists = [(sum(weeks.values()), artist) for artist, weeks in uh.artists.items()]
    artists.sort()
    artists.reverse()
    
    try:
        max_plays = float(artists[0][0])
    except IndexError:
        max_plays = 1000
    
    artists = [(plays, artist, 100*plays/max_plays) for plays, artist in artists]
    
    return render(request, "user_artists.html", {"username": username, "artists": artists})




def user_artist(request, username, artist):
    
    return render(request, "user_artist.html", {"username": username, "artist": artist})




def user_timeline(request, username):
    
    return render(request, "user_timeline.html", {"username": username})



def user_export(request, username):
    
    return render(request, "user_export.html", {"username": username})



def user_premium(request, username):
    
    lfuser = LastFmUser.by_username(username)
    
    return render(request, "user_premium.html", {"username": username, "lfuser": lfuser})



def user_premium_paid(request, username):
    
    lfuser = LastFmUser.by_username(username)
    
    return render(request, "user_premium_paid.html", {"username": username, "lfuser": lfuser})



def user_export_all_tabular(request, username, filetype):
    
    uh = UserHistory(username)
    uh.load_if_possible()
    
    data = [(("Week", {"bold":True}),("Artist", {"bold":True}),("Plays", {"bold":True}))]
    for week, artists in uh.weeks.items():
        for artist, plays in artists.items():
            data.append((week, artist, plays))
    
    try:
        return as_filetype(data, filetype, filename="%s_all" % username)
    except KeyError:
        raise Http404("No such filetype")


def user_export_all_json(request, username):
    
    uh = UserHistory(username)
    uh.load_if_possible()
    
    return jsonify({"username": username, "weeks":uh.weeks})


def user_export_artist_tabular(request, username, artist, filetype):
    
    uh = UserHistory(username)
    uh.load_if_possible()
    
    data = [(("Week", {"bold":True}),("Plays", {"bold":True}))]
    try:
        for week, plays in uh.artists[artist].items():
            data.append((week, plays))
    except KeyError:
        raise Http404("No such artist.")
    
    try:
        return as_filetype(data, filetype, filename="%s_%s" % (username, artist))
    except KeyError:
        raise Http404("No such filetype")


def user_export_artist_json(request, username, artist):
    
    uh = UserHistory(username)
    uh.load_if_possible()
    
    try:
        return jsonify({"username": username, "artist":artist, "weeks":uh.artists[artist]})
    except KeyError:
        raise Http404("No such artist.")



class NewPosterForm(forms.Form):
    
    start = forms.DateField(input_formats=("%Y/%m/%d",))
    end = forms.DateField(input_formats=("%Y/%m/%d",))
    
    style = forms.ChoiceField(choices=(
        ("ocean", "Ocean"),
        ("blue", "Blue"),
        ("desert", "Desert"),
        ("rainbow", "Rainbow"),
        ("sunset", "Sunset"),
        ("green", "Green"),
        ("eclectic", "Eclectic"),
    ))
    
    detail = forms.ChoiceField(choices=(
        ("1", "Super"),
        ("2", "High"),
        ("3", "Medium"),
        ("5", "Low"),
        ("10", "Terrible"),
        ("20", "Abysmal"),
        ("30", "Excrutiatingly Bad"),
    ))


def user_posters(request, username):
    
    user = LastFmUser.by_username(username)
    
    if "style" in request.POST:
        form = NewPosterForm(request.POST)
        if form.is_valid():
            poster = Poster(
                user = user,
                start = form.cleaned_data['start'],
                end = form.cleaned_data['end'],
                params = "%s|%s" % (form.cleaned_data['style'], form.cleaned_data['detail']),
                requested = datetime.datetime.now(),
            )
            poster.save()
            flash(request, "Poster request submitted. It is in queue position %i." % poster.queue_position())
            del form
            return HttpResponseRedirect("/user/%s/posters/?added=true" % username)
    
    if "form" not in locals():
        form = NewPosterForm({
            "start": (datetime.date.today() - datetime.timedelta(365)).strftime("%Y/%m/%d"),
            "end": datetime.date.today().strftime("%Y/%m/%d"),
            "detail": "3",
            "style": "ocean",
        })
    
    posters = user.posters.exclude(pdf_url="expired").order_by("-requested")
    
    return render(request, "user_posters.html", {
        "username": username,
        "posters": posters,
        "form": form,
    })

import json

from django.template.loader import select_template
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect as redirect
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import cache_page
from django.http import Http404


def render(request, template, params={}):
    ctx = RequestContext(request, params)
    
    if not isinstance(template, (list, tuple)):
        template = [template]
    
    return HttpResponse(select_template(template).render(ctx))


def jsonify(object):
    return HttpResponse("(%s)" % json.dumps(object))


def plaintext(string):
    return HttpResponse(unicode(string))


def flash(request, message):
    request.session['flashes'] = request.session.get('flashes', []) + [message]


def get_flashes(request):
    flashes = request.session.get('flashes', [])
    request.session['flashes'] = []
    return flashes


def contexter(request):
    return {
        "flashes": get_flashes(request),
    }

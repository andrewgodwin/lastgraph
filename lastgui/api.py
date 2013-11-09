
import datetime, time

from shortcuts import *

from lastgui.models import *
from lastgui.storage import UserHistory


# Some custom exceptions

class IncorrectPassword(Exception): pass

class BadData(Exception): pass

class MissingXML(Exception): pass



def valid_node(func):
	"""Decorator, which ensures the requester is a valid node."""
	def inner(request, *args, **kwds):
		nodename = request.REQUEST.get("nodename", None)
		password = request.REQUEST.get("password", None)
		
		# If they didn't provide, say so
		if not (nodename and password):
			return jsonify({"error":"authentication/missing"})
		
		# Get the Node and see if they have a match
		try:
			node = Node.objects.get(nodename=nodename)
			if not node.password_matches(password):
				raise IncorrectPassword
		except (Node.DoesNotExist, IncorrectPassword):
			return jsonify({"error":"authentication/invalid"})
		
		# Bung the node onto the request object
		request.node = node
		
		# Update it's lastseen
		node.lastseen = datetime.datetime.utcnow()
		node.save()
		
		# OK, all seems sensible
		return func(request, *args, **kwds)
	return inner


def datetime_to_epoch(dt):
	"""Turns a datetime.datetime into a seconds-since-epoch timestamp."""
	return time.mktime(dt.timetuple())

###################

@valid_node
def index(request):
	return jsonify({"server":"lastgraph/3.0"})


def graph_data(poster):
	
	uh = UserHistory(poster.user.username)
	uh.load_if_possible()
	
	# Get the start/end pairs of week times
	weeks = uh.weeks.keys()
	
	if not weeks:
		raise BadData("Empty")
	
	weeks.sort()
	weeks = zip(weeks, weeks[1:]+[weeks[-1]+7*86400])
	
	# Limit those to ones in the graph range
	pstart = datetime_to_epoch(poster.start)
	pend = datetime_to_epoch(poster.end)
	
	weeks = [(start, end) for start, end in weeks if (end > pstart) and (start < pend)]
	
	weekdata = [(start, end, uh.weeks[start].items()) for start, end in weeks]
	
	return weekdata


@valid_node
def render_next(request):
	
	"""
	Returns the next set of render data.
	"""
	
	# Get the Posters that needs rendering
	try:
		poster = Poster.queue()[0]
	except IndexError:
		return jsonify({"nothing":True})
	
	return render_data(request, poster.id)


@valid_node
def render_data(request, id=None):
	
	"""
	Returns a set of render data for the specified graph.
	"""
	
	if id is None:
		id = request.GET['id']
	
	poster = Poster.objects.get(id=id)
	
	# Compile a week data list
	try:
		weekdata = graph_data(poster)
	except BadData:
		poster.set_error("BadData")
		return jsonify({"nothing":True, "skipped":"%s/BadData" % poster.id})
	except MissingXML:
		poster.set_error("BadData")
		return jsonify({"nothing":True, "skipped":"%s/MissingXML" % poster.id})
	
	# Check it has data
	if len(weekdata) < 1:
		poster.set_error("No data (graph would be empty)")
		return jsonify({"nothing":True, "skipped":"%s/NoData" % poster.id})
	
	# Check it has data
	if len(weekdata) == 1:
		poster.set_error("Only one week of data (need two or more to graph)")
		return jsonify({"nothing":True, "skipped":"%s/OneWeek" % poster.id})
	
	poster.started = datetime.datetime.utcnow()
	poster.node = request.node
	poster.save()
	
	return jsonify({
		"id": poster.id,
		"username": poster.user.username,
		"start": int(time.mktime(poster.start.timetuple())),
		"end": int(time.mktime(poster.end.timetuple())),
		"params": poster.params,
		"data": weekdata,
	})


@valid_node
def render_links(request):
	
	id = request.POST['id']
	poster = Poster.objects.get(id=id)
	
	poster.pdf_url = request.POST['pdf_url']
	poster.svg_url = request.POST['svg_url']
	poster.completed = datetime.datetime.utcnow()
	poster.expires = datetime.datetime.utcnow() + datetime.timedelta(7)
	poster.save()
	
	return jsonify({"success":True})


@valid_node
def render_failed(request):
	
	"""
	Recieves downloaded week data.
	"""
	
	id = request.REQUEST['id']
	poster = Poster.objects.get(id=id)
	poster.set_error("Renderer error:\n%s" % request.REQUEST.get("traceback", "No traceback"))
	
	return jsonify({"recorded":True})
from django.conf.urls.defaults import *

urlpatterns = patterns('',
	
	# Front page
	(r'^$', 'lastgui.views.front'),
	
	# Help text, etc.
	(r'^about/$', 'django.views.generic.simple.direct_to_template', {'template': 'about.html'}),
	(r'^about/posters/$', 'django.views.generic.simple.direct_to_template', {'template': 'about_posters.html'}),
	(r'^about/posters/colours/$', 'django.views.generic.simple.direct_to_template', {'template': 'about_colours.html'}),
	(r'^about/artists/$', 'django.views.generic.simple.direct_to_template', {'template': 'about_artist_histories.html'}),
	(r'^crossdomain.xml$', 'django.views.generic.simple.direct_to_template', {'template': 'crossdomain.xml'}),
	
	# System status
	(r'^status/$', 'lastgui.views.status'),
	(r'^status/nagios/fetch/$', 'lastgui.views.status_nagios_fetch'),
	(r'^status/nagios/render/$', 'lastgui.views.status_nagios_render'),
	
	# User views
	(r'^user/([^/]+)/$', 'lastgui.views.user_root'),
	(r'^user/([^/]+)/artists/$', 'lastgui.views.user_artists'),
	(r'^user/([^/]+)/artist/(.*)/$', 'lastgui.views.user_artist'),
	(r'^user/([^/]+)/timeline/$', 'lastgui.views.user_timeline'),
	(r'^user/([^/]+)/posters/$', 'lastgui.views.user_posters'),
	(r'^user/([^/]+)/export/$', 'lastgui.views.user_export'),
	(r'^user/([^/]+)/premium/$', 'lastgui.views.user_premium'),
	(r'^user/([^/]+)/premium/paid/$', 'lastgui.views.user_premium_paid'),
	(r'^user/([^/]+)/sigs/$', 'lastgui.views.user_sigs'),
	
	(r'^user/([^/]+)/export/all\.json$', 'lastgui.views.user_export_all_json'),
	(r'^user/([^/]+)/export/all\.(csv|xls)$', 'lastgui.views.user_export_all_tabular'),
	(r'^user/([^/]+)/export/artist/(.*)\.json$', 'lastgui.views.user_export_artist_json'),
	(r'^user/([^/]+)/export/artist/(.*)\.(csv|xls)$', 'lastgui.views.user_export_artist_tabular'),
	
	# Ajax stuff
	(r'^ajax/([^/]+)/ready/$', 'lastgui.views.ajax_user_ready'),
	(r'^ajax/([^/]+)/queuepos/$', 'lastgui.views.ajax_user_queuepos'),
	
	# Graphs
	(r'^graph/([^/]+)/artist/([^/]+)/$', 'lastgui.views.graph_artist'),
	(r'^graph/([^/]+)/artist/([^/]+)/(\d+)/(\d+)/$', 'lastgui.views.graph_artist'),
	(r'^graph/([^/]+)/timeline/(\d+)/(\d+)/$', 'lastgui.views.graph_timeline'),
	(r'^graph/([^/]+)/timeline-basic/(\d+)/(\d+)/$', 'lastgui.views.graph_timeline_basic'),
	
	# Sigs
	(r'^graph/([^/]+)/sig1/$', 'lastgui.views.graph_sig1'),
	(r'^graph/([^/]+)/sig1/(\d+)/(\d+)/$', 'lastgui.views.graph_sig1'),
	
	# Render API
	(r'^api/$', 'lastgui.api.index'),
	(r'^api/render/next/$', 'lastgui.api.render_next'),
	(r'^api/render/data/(\d+)/$', 'lastgui.api.render_data'),
	(r'^api/render/links/$', 'lastgui.api.render_links'),
	(r'^api/render/failed/$', 'lastgui.api.render_failed'),
)
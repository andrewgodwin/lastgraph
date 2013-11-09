from django.contrib.admin import site
from .models import LastFmUser, Node, Poster

site.register(
    LastFmUser,
    list_display = ("id", "username", "requested_update", "last_check"),
    list_display_links = ("id", "username"),
    search_fields = ("username",),
    ordering = ("-last_check",),
)


site.register(
    Poster,
    list_display = ("id", "user", "requested", "completed", "failed"),
    ordering = ("-requested",),
)


site.register(
    Node,
    list_display = ("nodename", "disabled", "lastseen"),
)

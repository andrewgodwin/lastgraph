from django.db import models
import datetime
import random
import hashlib


class LastFmUser(models.Model):
    """
    Represents a user from that great site, last.fm.
    """
    
    # As seen on last.fm
    username = models.CharField(max_length=255, unique=True)
    
    # Null if no update wanted, else used to prioritise
    requested_update = models.DateTimeField(blank=True, null=True)
    
    # The last time this user was checked for updateness
    last_check = models.DateTimeField(blank=True, null=True)
    
    # Is this account enabled for external image access? And when till?
    external_until = models.DateTimeField(blank=True, null=True)
    
    # Is this already being fetched?
    fetching = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.username
    
    def get_absolute_url(self):
        return "/user/%s/" % self.username

    def external_allowed(self):
        return True  # I've become generous
        # if self.external_until:
        #     return self.external_until > datetime.datetime.utcnow()
        # else:
        #     return False
    
    @classmethod
    def by_username(cls, username):
        "Returns the correct object, possibly creating one."
        try:
            return cls.objects.get(username=username)
        except cls.DoesNotExist:
            instance = cls(username=username)
            instance.save()
            return instance
    
    @classmethod
    def queue(cls):
        "Returns the current update queue."
        return cls.objects.filter(requested_update__isnull=False).order_by("requested_update")


# IDs here ended with 27533
class Poster(models.Model):
    """
    A large poster. A shiny lastgraph2-esque PDF, like.
    """
    
    user = models.ForeignKey(LastFmUser, related_name="posters")
    
    start = models.DateField()
    end = models.DateField()
    
    params = models.TextField(blank=True)
    
    requested = models.DateTimeField(blank=True, null=True)
    started = models.DateTimeField(blank=True, null=True)
    completed = models.DateTimeField(blank=True, null=True)
    failed = models.DateTimeField(blank=True, null=True)
    expires = models.DateTimeField(blank=True, null=True)
    
    email = models.TextField(blank=True)
    
    error = models.TextField(blank=True)
    
    node = models.ForeignKey("Node", blank=True, null=True)
    
    pdf_url = models.TextField(blank=True)
    svg_url = models.TextField(blank=True)
    
    def __unicode__(self):
        return u"%s: %s - %s" % (self.user, self.start, self.end)
    
    def queue_position(self):
        queue = list(Poster.queue())
        try:
            return queue.index(self) + 1
        except (IndexError, ValueError):
            return len(queue) + 1
    
    def status_string(self):
        if self.failed:
            return "Failed"
        if self.requested:
            if self.completed:
                if self.pdf_url == "expired":
                    return "Expired"
                else:
                    return "Complete"
            elif self.started:
                return "Rendering"
            return "Queued, position %i" % self.queue_position()
        return "Unrequested"
    
    def expired(self):
        return self.completed and self.pdf_url == "expired"
    
    def detail_string(self):
        detail = int(self.params.split("|")[1])
        return {
            1: "Super",
            2: "High",
            3: "Medium",
            5: "Low",
            10: "Terrible",
            20: "Abysmal",
            30: "Excrutiatingly Bad",
        }.get(detail, detail)
    
    def colorscheme_string(self):
        return self.params.split("|")[0].title()
    
    def set_error(self, error):
        self.error = error
        self.failed = datetime.datetime.utcnow()
        self.save()
    
    @classmethod
    def queue(cls):
        return cls.objects.filter(requested__isnull=False, started__isnull=True, failed__isnull=True).order_by("requested")


class Node(models.Model):
    
    """Represents a processing node, i.e. something that either downloads or renders data."""
    
    nodename = models.CharField('Node name', max_length=100, unique=True)
    salt = models.CharField('Password salt', max_length=20)
    hash = models.CharField('Password hash', max_length=100)
    
    disabled = models.BooleanField(default=False)
    lastseen = models.DateTimeField('Last seen', null=True, blank=True, default=None)
    
    def __unicode__(self):
        return "Node '%s'" % self.nodename
    
    def set_password(self, password):
        self.salt = "".join([random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for i in range(8)])
        self.hash = hashlib.sha1(self.salt + password).hexdigest()
    
    def password_matches(self, password):
        return self.hash == hashlib.sha1(self.salt + password).hexdigest()
    
    @classmethod
    def recent(cls):
        return cls.objects.filter(lastseen__gte=datetime.datetime.utcnow() - datetime.timedelta(0, 5*60))

import sys
from django.core.management import BaseCommand
from lastgui.models import *
from lastgui.fetch import update_user


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        # Get the top person in the queue
        queue = LastFmUser.queue().filter(fetching=False)
        try:
            user = queue[0]
        except IndexError:
            print "No users queued."
            sys.exit(2)
        
        print "Updating user '%s'..." % user.username
        user.fetching = True
        user.save()
        
        try:
            # Download their data!
            update_user(user.username)
            
            # Mark them as done!
            user.requested_update = None
            user.fetching = False
            user.save()
            print "Done!"
        except AssertionError, e:
            print "Oh well, we'll ignore them."
            user.requested_update = None
            user.fetching = False
            user.save()
            raise e
        except UnicodeDecodeError, e:
            print "Unicode error. Uh-oh."
            print user.username
            user.fetching = False
            user.save()
        except Exception,e:
            user.fetching = False
            user.save()
            print "Restored user in queue"
            raise e

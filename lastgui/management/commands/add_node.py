import sys
from django.core.management import BaseCommand
from lastgui.models import Node


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        # Error if we don't understand
        if len(args) != 2:
            print "Usage: add_node <nodename> <password>"
            sys.exit(1)
        # Add the node
        node = Node(nodename=args[0])
        node.set_password(args[1])
        node.save()
        print "Node %s added" % node.nodename

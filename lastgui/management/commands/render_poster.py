import sys
from django.core.management import BaseCommand
from lastrender.renderer import render_poster


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        render_poster()

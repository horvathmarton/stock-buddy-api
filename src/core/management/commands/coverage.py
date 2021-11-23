from os import system

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Displays the test coverage report for the project."

    def handle(self, *args, **kwargs):
        self.stdout.write(ending="\n")

        self.stdout.write("-------- Running coverage report. --------", ending="\n\n")
        system("coverage run --source='src' manage.py test src")
        system("coverage report")
        self.stdout.write(ending="\n\n")

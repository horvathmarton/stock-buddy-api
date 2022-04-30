"""Test coverage command for the project."""

from os import system

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Custom command to check test coverage of the project."""

    help = "Displays the test coverage report for the project."

    def handle(self, *args, **kwargs):
        self.stdout.write(ending="\n")

        self.stdout.write("-------- Running coverage report. --------", ending="\n\n")
        system("coverage run manage.py test src")  # nosec
        system("coverage report")  # nosec
        self.stdout.write(ending="\n\n")

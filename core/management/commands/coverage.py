"""Test coverage command for the project."""

from os import system

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Custom command to check test coverage of the project."""

    help = "Displays the test coverage report for the project."

    def handle(self, *args, **kwargs):
        TARGET_FOLDERS = " ".join(("apps", "lib"))

        self.stdout.write(ending="\n")

        self.stdout.write("-------- Running coverage report. --------", ending="\n\n")
        system(  # nosec - Target folders are fixed.
            f"coverage run manage.py test {TARGET_FOLDERS}"
        )
        system("coverage report")  # nosec - Fixed command.
        self.stdout.write(ending="\n\n")

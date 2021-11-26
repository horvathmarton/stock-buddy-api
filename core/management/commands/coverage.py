from os import system

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Displays the test coverage report for the project."

    def handle(self, *args, **kwargs):
        target_folders = " ".join(("apps", "lib"))

        self.stdout.write(ending="\n")

        self.stdout.write("-------- Running coverage report. --------", ending="\n\n")
        system(f"coverage run manage.py test {target_folders}")
        system("coverage report")
        self.stdout.write(ending="\n\n")

from os import system

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Format, lint and type check the code. (black, flake8, pylint, mypy, bandit)"

    def handle(self, *args, **kwargs):
        target_folders = " ".join(("apps", "config", "core", "lib"))

        self.stdout.write(ending="\n")

        self.stdout.write(
            "-------- Formatting the code using black. --------", ending="\n\n"
        )
        black = self._result(system(f"black {target_folders}"))
        self.stdout.write(ending="\n\n")

        self.stdout.write("-------- Linting code using flake8. --------", ending="\n\n")
        flake8 = self._result(system(f"flake8 {target_folders}"))
        self.stdout.write(ending="\n\n")

        self.stdout.write("-------- Linting code using pylint. --------", ending="\n\n")
        pylint = self._result(system(f"pylint {target_folders}"))
        self.stdout.write(ending="\n\n")

        self.stdout.write(
            "-------- Type checking code using mypy. --------", ending="\n\n"
        )
        mypy = self._result(system(f"mypy {target_folders}"))
        self.stdout.write(ending="\n\n")

        # TODO: This should be integrated later, but for now it only provides false positives.
        # TODO: The return value is also not usable as it is always 0.
        # self.stdout.write("-------- Analyzing code using bandit. --------", ending="\n\n")
        # bandit = self._result(system(f"bandit -r {target_folder}"))
        # self.stdout.write(ending="\n\n")

        self.stdout.write(f"{black=} {flake8=} {pylint=} {mypy=}\n\n")

    @staticmethod
    def _result(exit_code) -> str:
        return "❌" if exit_code else "🔥"

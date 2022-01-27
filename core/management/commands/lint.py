"""Linter command for the project."""

from os import system

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Custom command to run formatters and linters on the project."""

    help = "Format, lint and type check the code. (black, flake8, pylint, mypy, bandit)"

    def handle(self, *args, **kwargs):
        TARGET_FOLDERS = " ".join(("apps", "config", "core", "lib"))

        self.stdout.write(ending="\n")

        self.stdout.write(
            "-------- Formatting the code using black. --------", ending="\n\n"
        )
        black = self._result(
            system(f"black {TARGET_FOLDERS}")  # nosec - Target folders are fixed.
        )
        self.stdout.write(ending="\n\n")

        self.stdout.write(
            "-------- Analyzing code using bandit. --------", ending="\n\n"
        )
        bandit = self._result(
            system(f"bandit -r {TARGET_FOLDERS}")  # nosec - Target folders are fixed.
        )
        self.stdout.write(ending="\n\n")

        self.stdout.write(
            "-------- Type checking code using mypy. --------", ending="\n\n"
        )
        mypy = self._result(
            system(f"mypy {TARGET_FOLDERS}")  # nosec - Target folders are fixed.
        )
        self.stdout.write(ending="\n\n")

        self.stdout.write("-------- Linting code using flake8. --------", ending="\n\n")
        flake8 = self._result(
            system(f"flake8 {TARGET_FOLDERS}")  # nosec - Target folders are fixed.
        )
        self.stdout.write(ending="\n\n")

        self.stdout.write("-------- Linting code using pylint. --------", ending="\n\n")
        pylint = self._result(
            system(f"pylint {TARGET_FOLDERS}")  # nosec - Target folders are fixed.
        )
        self.stdout.write(ending="\n\n")

        self.stdout.write(
            f"{black=} {flake8=} {pylint=} {mypy=} {bandit=}", ending="\n\n"
        )

    @staticmethod
    def _result(exit_code: int) -> str:
        """Map the result exit code to a proper emoji."""

        return "❌" if exit_code else "🔥"

from os import system

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Format, lint and type check the code. (black, flake8, pylint, mypy, bandit)"

    def handle(self, *args, **kwargs):
        self.stdout.write("-------- Formatting the code using black. --------\n\n")
        black = self._result(system("black src config"))
        self.stdout.write("\n\n")

        self.stdout.write("-------- Linting code using flake8. --------\n\n")
        flake8 = self._result(system("flake8 src config"))
        self.stdout.write("\n\n")

        self.stdout.write("-------- Linting code using pylint. --------\n\n")
        pylint = self._result(system("pylint src config"))
        self.stdout.write("\n\n")

        self.stdout.write("-------- Type checking code using mypy. --------\n\n")
        mypy = self._result(system("mypy src config"))
        self.stdout.write("\n\n")

        # TODO: This should be integrated later, but for now it only provides false positives.
        # TODO: The return value is also not usable as it is always 0.
        # self.stdout.write("-------- Analyzing code using bandit. --------\n\n")
        # bandit = self._result(system("bandit -r src config"))
        # self.stdout.write("\n\n")

        self.stdout.write(f"{black=} {flake8=} {pylint=} {mypy=}\n\n")

    @staticmethod
    def _result(exit_code) -> str:
        return "❌" if exit_code else "🔥"

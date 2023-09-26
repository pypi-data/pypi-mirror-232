import argparse
from django.core.management.base import BaseCommand
from django_swagger_utils.server.generators.build_app import build


class Command(BaseCommand):
    help = 'My custom Django management command'

    def add_arguments(self, parser):
        # Add other command-specific options as needed
        parser.add_argument("--app", help="Command-specific option")

    def handle(self, *args, **kwargs):
        print("options", kwargs)
        if kwargs.get('app'):
            build(kwargs)
        else:
            print("Invalid command. app name not provided.")


if __name__ == "__main__":
    Command().execute()

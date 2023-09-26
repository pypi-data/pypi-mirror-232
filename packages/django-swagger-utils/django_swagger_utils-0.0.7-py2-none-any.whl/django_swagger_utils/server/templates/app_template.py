import exceptions
import os
import re
from os import path
from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django_swagger_utils.server.constants.app_structure import APP_STRUCTURE


class TemplateCommand(BaseCommand):
    def __init__(self, stdout=None, stderr=None, no_color=False):
        super(TemplateCommand, self).__init__(stdout, stderr, no_color)
        self.app_path = None
        self.parent_directory = None
        self.app = None
        self.app_name = None

    def add_arguments(self, parser):
        parser.add_argument("--app", help="Command-specific option")

    def handle(self, app, app_name, **options):
        self.app = app
        self.app_name = app_name
        self.parent_directory = os.getcwd()

        if self.is_app_exists(app_name):
            self.stdout.write(self.style.ERROR("Error: App exists with given name"))
        else:
            try:
                if self.validate_app_name(app_name):
                    self.create_directory(self.app_path, app_name)
                    self.app_path = path.join(self.parent_directory, app_name)
                    self.create_subdirectory(self.app_path)
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            "Error: App names must begin with an alphabet or underscore "
                            "and may consist of alphabets, numbers, and underscores.")
                    )
            except exceptions.OSError as e:
                self.stdout.write(self.style.ERROR("Error: {}".format(e)))

    @staticmethod
    def is_app_exists(app_name):
        if apps.is_installed(app_name):
            return True
        else:
            project_directory = os.path.dirname(os.path.abspath(__file__))

            for root, dirs, files in os.walk(project_directory):
                for dir_name in dirs:
                    if dir_name == app_name:
                        print("The app '{}' is found in directory: {}".format(app_name, os.path.join(root, dir_name)))
                        return True
        return False

    @staticmethod
    def validate_app_name(app_name):
        pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*$'
        return re.match(app_name, pattern)

    @staticmethod
    def create_init_file(directory):
        init_file_path = os.path.join(directory, "__init__.py")
        open(init_file_path, "").close()

    def create_directory(self, directory, app_name):
        os.mkdir(directory, app_name)
        self.create_init_file(directory)

    def create_subdirectory(self, sub_directory):
        for module in APP_STRUCTURE:
            os.mkdir(sub_directory, module)
            self.create_init_file(sub_directory)
            for sub_module in module:
                os.mkdir(sub_directory, sub_module)
                self.create_init_file(sub_directory)

    @staticmethod
    def write_content(file_path, file_name, content):
        pass

import os
import re
from os import path
from django.core.management.base import BaseCommand
from django_swagger_utils.server.templates.app_config import APP_CONFIG
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

        try:
            if self.validate_app_name(app_name):
                self.app_path = path.join(self.parent_directory, app_name)
                try:
                    self.create_directory(self.app_path)
                    self.create_subdirectory(self.app_path)
                    self.create_app_files(self.app_path)
                except OSError as e:
                    # Handle the error appropriately, e.g., log it
                    self.stderr.write(self.style.ERROR("Error creating app directory: {}".format(e)))
                    # Remove the directory if it was partially created
                    os.rmdir(self.app_path)
            else:
                self.stderr.write(
                    self.style.ERROR(
                        "Error: App names must begin with an alphabet or underscore "
                        "and may consist of alphabets, numbers, and underscores.")
                )
        except OSError as e:
            self.stderr.write(self.style.ERROR("Error: {}".format(e)))

    @staticmethod
    def validate_app_name(app_name):
        pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*$'
        return re.match(pattern, app_name)

    @staticmethod
    def create_file(directory, file_name, content=''):
        with open(os.path.join(directory, file_name), 'w') as file:
            file.write(content)

    def create_directory(self, directory):
        os.mkdir(directory)
        self.create_file(directory, "__init__.py")

    def create_subdirectory(self, sub_directory):
        for module in APP_STRUCTURE:
            module_path = os.path.join(sub_directory, module)
            os.mkdir(module_path)
            self.create_file(module_path, "__init__.py")
            for sub_module in APP_STRUCTURE.get(module):
                for each_file in sub_module:
                    sub_module_path = os.path.join(module_path, each_file)
                    os.mkdir(sub_module_path)
                    self.create_file(sub_module_path, "__init__.py")

    def create_app_files(self, app_directory):
        for app_file in ['app.py', 'admin.py', 'db_dicts.py', 'db_fixtures.py']:
            self.create_file(app_directory, app_file)
        app_config_code = APP_CONFIG.replace("{{app}}", self.app_name)
        self.create_file(app_directory, 'app.py', app_config_code)
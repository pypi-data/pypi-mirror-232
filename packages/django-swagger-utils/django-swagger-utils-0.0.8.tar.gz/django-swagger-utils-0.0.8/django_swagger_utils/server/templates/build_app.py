import json
import os
import re
from os import path
from django.core.management.base import BaseCommand
from django_swagger_utils.server.generators.url_generator import GenerateURLPatterns
from ..generators.app_view_generator import *

class TemplateCommand(BaseCommand):
    def __init__(self, stdout=None, stderr=None, no_color=False):
        super(TemplateCommand, self).__init__(stdout, stderr, no_color)
        self.app_path = None
        self.parent_directory = None
        self.app = None
        self.app_name = None
        self.swagger_spec = {}

    def add_arguments(self, parser):
        parser.add_argument("--app", help="Command-specific option")

    def handle(self, app, app_name, **options):
        self.app = app
        self.app_name = app_name
        self.parent_directory = os.getcwd()
        try:
            self.swagger_spec = self.get_api_spec()
            self.validate_swagger_spec(self.swagger_spec)
            self.generate_urls(self.swagger_spec)
        except OSError:
            os.rmdir(self.app_name)

    def get_api_spec(self):
        file_path = "{}/api_specs".format(self.app_name)
        with open(os.path.join(file_path, 'api_spec.json'), 'r') as file:
            file_contents = file.read()
        return file_contents

    def validate_swagger_spec(self, swagger_spec):
        swagger_data = json.loads(swagger_spec)
        url_paths = swagger_data.get('paths')
        self.generate_urls(url_paths)
        for item in url_paths:
            print(item)

    def generate_views(self):
        generator = APIViewGenerator(self.app_name, self.swagger_spec.get('paths'))
        generator.generate_views()

    def generate_urls(self, paths):
        generator = GenerateURLPatterns(self.app_name, paths)
        generator.generate_url_patterns()

    def generate_serializers(self, views):
        pass
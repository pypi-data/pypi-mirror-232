# application/management/commands/generate_crud.py
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.apps import apps


class Command(BaseCommand):
    help = 'Generate CRUD views and URLs for a given model'

    def add_arguments(self, parser):
        parser.add_argument('app_label', help='The app containing the model')
        parser.add_argument('model_name', help='The name of the model')

    def handle(self, *args, **kwargs):
        app_label = kwargs['app_label']
        model_name = kwargs['model_name']

        try:
            model = apps.get_model(app_label, model_name)
        except LookupError:
            self.stderr.write(self.style.ERROR(f"Model '{model_name}' in app '{app_label}' not found."))
            return

        # Generate CRUD views and URLs
        self.stdout.write(self.style.SUCCESS(f"Generating CRUD views and URLs for '{model_name}' in app '{app_label}'..."))
        call_command('generate_crud_views', app_label, model_name)
        self.stdout.write(self.style.SUCCESS(f"CRUD views and URLs generated successfully for '{model_name}' in app '{app_label}'."))

# myapp/management/commands/generate_crud_views.py
import os
import re

from django.core.management.base import BaseCommand
from django.apps import apps


class Command(BaseCommand):
    help = 'Generate CRUD Views and Serializers for a given model'

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

        # Generate and save the serializer class dynamically
        serializer_name = f'{model_name}Serializer'
        serializer_class_code = f'''

class {serializer_name}(serializers.ModelSerializer):
    class Meta:
        model = {model_name}
        fields = '__all__'
'''
        # Define the imports you want to add
        imports_to_add = {
            f'from rest_framework import serializers',
            f'from .models import {model_name}',
        }

        # Save the serializer class to a Python file (e.g., serializers.py)
        serializers_file_path = f'{app_label}/serializers.py'
        # Check if the file exists
        if not os.path.exists(serializers_file_path):
            with open(serializers_file_path, 'w') as serializers_file:
                serializers_file.write(serializer_class_code)
        else:
            # Check if the serializer class code already exists in the file
            with open(serializers_file_path, 'r') as serializers_file:
                existing_code = serializers_file.read()

            # Check if the serializer_name is in the existing code
            for import_statement in imports_to_add:
                if import_statement not in existing_code:
                    # If an import is not present, add it at the beginning of the file
                    # You can choose to add it at the top or just before the class definition, depending on your preference
                    if re.match(r'^\s*class', existing_code, re.MULTILINE):
                        # Add before the class definition
                        existing_code = existing_code.replace(
                            f'class {serializer_name}(serializers.ModelSerializer):',
                            f'{import_statement}\n\nclass {serializer_name}(serializers.ModelSerializer):',
                            1
                        )
                    else:
                        # Add at the top of the file
                        existing_code = f'{import_statement}\n\n{existing_code}'
            # Check if the viewset class code already exists in the file
            if serializer_name not in existing_code:
                # Append the new viewset class to the existing file
                with open(serializers_file_path, 'w') as views_file:
                    views_file.write(existing_code)
                    views_file.write('\n\n')
                    views_file.write(serializer_class_code)
            else:
                print("Serializer class already exists in the file.")

        # Generate and save the viewset class dynamically
        viewset_name = f'{model_name}ViewSet'
        viewset_class_code = f'''

class {viewset_name}(viewsets.ModelViewSet):
    queryset = {model_name}.objects.all()
    serializer_class = {model_name}Serializer
'''
        # Define the imports you want to add
        imports_to_add = {
            f'from rest_framework import viewsets',
            f'from .models import {model_name}',
            f'from .serializers import {model_name}Serializer'
        }
        # Save the serializers class to a Python file (e.g., views.py)
        views_file_path = f'{app_label}/views.py'
        # Check if the file exists
        if not os.path.exists(views_file_path):
            with open(views_file_path, 'w') as views_file:
                views_file.write(viewset_class_code)
        else:
            # Read the existing code from the file
            with open(views_file_path, 'r') as views_file:
                existing_code = views_file.read()

            # Check if the imports are already present in the file
            for import_statement in imports_to_add:
                if import_statement not in existing_code:
                    # If an import is not present, add it at the beginning of the file
                    # You can choose to add it at the top or just before the class definition, depending on your preference
                    if re.match(r'^\s*class', existing_code, re.MULTILINE):
                        # Add before the class definition
                        existing_code = existing_code.replace(
                            f'class {viewset_name}(viewsets.ModelViewSet):',
                            f'{import_statement}\n\nclass {viewset_name}(viewsets.ModelViewSet):',
                            1
                        )
                    else:
                        # Add at the top of the file
                        existing_code = f'{import_statement}\n\n{existing_code}'

            # Check if the viewset class code already exists in the file
            if viewset_name not in existing_code:
                # Append the new viewset class to the existing file
                with open(views_file_path, 'w') as views_file:
                    views_file.write(existing_code)
                    views_file.write('\n\n')
                    views_file.write(viewset_class_code)
            else:
                print("Viewset class already exists in the file.")

        # Generate URL patterns for the viewset
        urlpatterns_code = f'''
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import {model_name}ViewSet

# Check if the router is not defined already
if 'router' not in locals():
    router = DefaultRouter()
router.register('{model_name.lower()}', {model_name}ViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
'''
        # Save the URL patterns to a Python file (e.g., urls.py)
        urls_file_path = f'{app_label}/urls.py'

        # Check if the urls file exists
        if os.path.exists(urls_file_path):
            with open(urls_file_path, 'r') as urls_file:
                existing_code = urls_file.read()

            # Check if both model_name and urlpatterns_code are not in the existing code
            if model_name not in existing_code and urlpatterns_code not in existing_code:
                # Find the starting and ending index of the urlpatterns list
                start_index = existing_code.find("urlpatterns = [")
                end_index = existing_code.find("]", start_index)

                if start_index != -1 and end_index != -1:
                    # Remove the existing urlpatterns list (including brackets and indentation)
                    existing_code = existing_code[:start_index] + existing_code[end_index + 1:]

                    # Append the new urlpatterns code to the existing file
                    with open(urls_file_path, 'w') as urls_file:
                        urls_file.write(existing_code.strip() + '\n\n' + urlpatterns_code)

                else:
                    print("Couldn't find the 'urlpatterns' list in the urls file.")
            else:
                print("URL patterns or model_name already exist in the urls file.")
        else:
            print(f"The urls file '{urls_file_path}' does not exist.")

        self.stdout.write(self.style.SUCCESS(f"CRUD Views generated successfully for '{model_name}' in app '{app_label}'"))

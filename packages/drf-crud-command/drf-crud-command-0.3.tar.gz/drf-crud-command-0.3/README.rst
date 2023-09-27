
Quick Start
===========

1. Add "crud_management" to your INSTALLED_APPS setting like this:

    INSTALLED_APPS = [

        ...
        'crud_management',


    ]

2. Run ``python manage.py migrate`` to create the user models


3. You need to create a url.py and serializers.py file in your applications

4. Run ``python manage.py generate_crud`` <your_app_name> <your_model>

5. Start the development server and visit http://127.0.0.1:8000/ to create a new user login register
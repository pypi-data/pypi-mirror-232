=================
Customers
=================

A Django app to create customers.


Quick start
-----------

1. Install the required packages:

    ``pip install django-json-widget artd-location artd-partner``

2. Add apps to your INSTALLED_APPS setting like this:
    
        INSTALLED_APPS = [
            ...
            "artd_location",
            "artd_partner",
            "django_json_widget",
            "artd_customer",
            ...
        ]

3. Run ``python manage.py migrate`` to create the product models.

4. Run ``python manage.py create_countries`` to create countries.

5. Run ``python manage.py create_colombian_regions`` to create colombian regions.

6. Run ``python manage.py create_colombian_cities`` to create colombian cities.

7. Start the development server and visit http://127.0.0.1:8000/admin/
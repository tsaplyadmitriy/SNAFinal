import os

from django.conf import settings

from .celery import celery_app

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
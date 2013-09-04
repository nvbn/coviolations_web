from django.conf import settings

for module in settings.SERVICES:
    __import__(module)

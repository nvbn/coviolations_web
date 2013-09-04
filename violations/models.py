from django.conf import settings

for module in settings.VIOLATIONS:
    __import__(module)

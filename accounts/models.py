from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext as _
from userena.models import UserenaBaseProfile


class Profile(UserenaBaseProfile):
    """Profile"""
    user = models.OneToOneField(
        User, verbose_name=_('user'), unique=True, related_name='profile',
    )

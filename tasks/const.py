from django.utils.translation import ugettext_lazy as _


STATUS_NEW = 0
STATUS_SUCCESS = 1
STATUS_FAILED = 2

STATUSES = (
    (STATUS_NEW, _('new')),
    (STATUS_SUCCESS, _('success')),
    (STATUS_FAILED, _('failed')),
)

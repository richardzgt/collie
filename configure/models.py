import logging
import traceback

from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _
from common.clients import ZBXClient

LOG = logging.getLogger('collie')


# Create your models here.

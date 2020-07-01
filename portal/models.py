import uuid
import logging
import traceback

from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import UserManager as DjangoUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from common.clients import ZBXClient


LOG = logging.getLogger('collie')


class UserManager(DjangoUserManager):

    def _create_user(self, company, email, password, **extra_fields):
        """
        Create and save a user with the given company, email, and password.
        """
        if not company:
            raise ValueError('The given company must be set')
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(company=company, email=email,
                          **extra_fields)
        user.set_password(password)
        return user.save(using=self._db)

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email=email,
                                 password=password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(username=username, email=email,
                                 password=password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        }
    )

    company = models.CharField(
        _('company'),
        max_length=150,
        help_text=_('Required. 150 characters or fewer.')
    )
    email = models.EmailField(_('email address'), blank=False, null=False,
                              unique=True, db_index=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.')
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    quota = models.IntegerField(_('instance quota'), blank=True,
                                null=True, db_index=True, default=0,
                                help_text='可监控的实例个数')
    expire_date = models.DateTimeField(_('expire date'), db_index=True,
                                       help_text='套餐到期时间')

    objects = UserManager()

    zbx_uid = models.IntegerField('Zabbix userid', blank=True, null=True, default=0)
    zbx_gid = models.IntegerField('Zabbix hostgroupid', blank=True, null=True, default=0)

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['company', 'email']

    @property
    def is_available(self):
        """套餐未到期且已监控实例数小于限额则视为可用"""
        # TODO 获取已监控实例数
        return self.expire_date > timezone.now() and self.quota > 0

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super().save(force_insert=force_insert,
                     force_update=force_update,
                     using=using, update_fields=update_fields)
        if not (self.zbx_uid or self.is_staff):
            # guest
            try:
                self.zbx_uid = ZBXClient.user.create(alias=str(self.id),
                                                     passwd='collie',
                                                     usrgrps=[{'usrgrpid': 8}]
                                                     )['userids'][0]
                self.zbx_gid = ZBXClient.hostgroup.create(name=str(self.id))['groupids'][0]
                super().save()
            except Exception as e:
                LOG.error(f'failed to create zabbix user or hostgroup for {self.id}: {traceback.format_exc()}')
                raise e
        return self

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        return str(self.username)

    def get_username(self):
        return str(self.username)

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

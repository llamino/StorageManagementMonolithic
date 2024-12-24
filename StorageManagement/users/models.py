from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field is required.'))
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if not extra_fields.get('is_staff'):
            raise ValueError(_('Superuser must have is_staff=True.'))
        if not extra_fields.get('is_superuser'):
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(max_length=11, unique=True, verbose_name=_('Phone Number'))
    email = models.EmailField(unique=True, verbose_name=_('Email'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    is_staff = models.BooleanField(default=False, verbose_name=_('Staff Status'))
    is_superuser = models.BooleanField(default=False, verbose_name=_('Superuser Status'))
    create_date = models.DateTimeField(auto_now_add=True, verbose_name=_('Date Created'))
    update_date = models.DateTimeField(auto_now=True, verbose_name=_('Date Updated'))

    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_groups',
        blank=True,
        verbose_name=_('Groups')
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions',
        blank=True,
        verbose_name=_('User Permissions')
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number']

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return self.email

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='profile_pics', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.email

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    province = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    street = models.CharField(max_length=50, blank=True, null=True)
    alley = models.CharField(max_length=50, blank=True, null=True)
    house_number = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f'{self.user.email} {self.id}'

@receiver(post_save, sender=User)
def save_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from rest_framework.authtoken.models import Token


class UserBase(models.Model):
    created_at = models.DateTimeField("Criado em", default=timezone.now)
    updated_at = models.DateTimeField("Alterado em", auto_now=True)

    class Meta:
        abstract = True


class UserManager(BaseUserManager):
    def _create_user(self, whatsapp, password, **extra_fields):
        if not whatsapp:
            raise ValueError("The given whatsapp must be set")
        #  if not whatsapp_is_valid(whatsapp): # TODO
            #  raise ValueError("The given whatsapp must be valid")
        user = self.model(whatsapp=whatsapp, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        Token.objects.create(user=user)
        return user

    def create_user(self, whatsapp, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_staff", False)
        return self._create_user(whatsapp, password, **extra_fields)

    def create_superuser(self, whatsapp, password, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(whatsapp, password, **extra_fields)


class UserModel(UserBase, AbstractBaseUser, PermissionsMixin):
    name = models.CharField("User's name", max_length=100)
    whatsapp = models.CharField("Whatsapp", max_length=20, unique=True)
    is_staff = models.BooleanField(
        "staff status",
        default=False,
        help_text="Designates whether the user can log into this admin site.",
    )
    is_active = models.BooleanField(
        "active",
        default=True,
        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
    )

    USERNAME_FIELD = "whatsapp"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f"User: {self.name} "

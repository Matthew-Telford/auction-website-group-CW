from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

# Create your models here.


class MyUserManager(BaseUserManager):
    def create_user(self, first_name, last_name, email, date_of_birth, password=None):
        if not email:
            raise ValueError("Users must have an email address")
        user = self.model(
            first_name=first_name,
            last_name=last_name,
            email=self.normalize_email(email),
            date_of_birth=date_of_birth,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, email, date_of_birth, password=None):
        user = self.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            date_of_birth=date_of_birth,
        )
        user.is_admin = True
        user.is_superuser = True
        # is_staff is a property that returns is_admin, so no need to set it explicitly
        user.save(using=self._db)
        return user


class User(AbstractUser):
    # Remove username field since we're using email as USERNAME_FIELD
    username = None
    # first_name and last_name already exist in AbstractUser, no need to redefine
    date_of_birth = models.DateField()
    email = models.EmailField(verbose_name="email address", max_length=254, unique=True)
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        null=True,
        blank=True,
        help_text="User's profile picture"
    )
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = MyUserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["date_of_birth", "first_name", "last_name"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        return self.is_admin

    pass


class PageView(models.Model):
    count = models.IntegerField(default=0)

    def __str__(self):
        return f"Page view count: {self.count}"

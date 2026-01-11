from django.db import models
import datetime
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db.models import F, Q

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

    def create_superuser(
        self, first_name, last_name, email, date_of_birth, password=None
    ):
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
        upload_to="profile_pictures/",
        null=True,
        blank=True,
        help_text="User's profile picture",
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


class Item(models.Model):
    title = models.CharField(max_length=80)
    description = models.TextField(max_length=1250)
    # Allow the owner column to store a null value as if the owner deletes there account after an auction has ended we still want record of the auction
    owner = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL, related_name="owned_items"
    )
    # Allow the auction_winner column to store a null value as if the auction_winner deletes there account after an auction has ended we still want
    # record of the auction
    auction_winner = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL, related_name="won_items"
    )
    minimum_bid = models.IntegerField()
    auction_end_date = models.DateField()
    item_image = models.ImageField(
        upload_to="item_pictures/",
        null=True,
        blank=True,
        help_text="Auction item photo",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    REQUIRED_FIELDS = [
        "title",
        "description",
        "owner",
        "minimum_bid",
        "auction_end_date",
    ]

    class Meta:
        indexes = [
            models.Index(fields=["title"], name="title_idx"),
            models.Index(fields=["description"], name="description_idx"),
            models.Index(fields=["-created_at"], name="created_at_idx"),
        ]

    def __str__(self):
        return self.title


class Bid(models.Model):
    bidder = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    bid_amount = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    REQUIRED_FIELDS = [
        "bidder",
        "item",
        "bid_amount",
    ]


class Message(models.Model):
    poster = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="sent_messages"
    )
    replying_to = models.ForeignKey("Message", null=True, blank=True, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    message_title = models.CharField(max_length=80)
    message_body = models.TextField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)
    REQUIRED_FIELDS = [
        "poster",
        "item",
        "message_title",
        "message_body",
    ]

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.replying_to and self.replying_to.item != self.item:
            raise ValidationError(
                "Reply must be connected to the same item as the parent message"
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.message_title


class PageView(models.Model):
    count = models.IntegerField(default=0)

    def __str__(self):
        return f"Page view count: {self.count}"

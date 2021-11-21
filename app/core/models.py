from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
    PermissionsMixin
from django.conf import settings
from django.utils.translation import gettext as _
from model_utils.fields import AutoCreatedField, AutoLastModifiedField
import datetime
from safedelete.models import SafeDeleteModel
from safedelete.managers import SafeDeleteManager
from safedelete import DELETED_INVISIBLE
from safedelete.models import SOFT_DELETE, HARD_DELETE


class MyModelManager(SafeDeleteManager):
    _safedelete_visibility = DELETED_INVISIBLE


class BaseModel(SafeDeleteModel):
    """
    An abstract base class model that provides self-updating
    ``created`` and ``modified`` fields.

    """
    _safedelete_policy = SOFT_DELETE
    created = AutoCreatedField(_('created'))
    modified = AutoLastModifiedField(_('modified'))
    is_active = models.BooleanField(default=True)
    objects = MyModelManager()

    class Meta:
        abstract = True

    def delete(self, force_policy=None, **kwargs):
        if self.deleted is not None:
            super().delete(force_policy=HARD_DELETE, **kwargs)
        else:
            super().delete(force_policy, **kwargs)


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """Creates and saves a new user"""
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """Creates and saves a new superuser"""
        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class Country(BaseModel):
    """List of country"""
    name = models.CharField(max_length=255)

    def __str__(self):
        return 'Country: %s' % (self.name)


class State(BaseModel):
    """List of state"""
    name = models.CharField(max_length=255)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    def __str__(self):
        return 'State: %s' % (self.name)


class City(BaseModel):
    """List of city"""
    name = models.CharField(max_length=255)
    state = models.ForeignKey(State, on_delete=models.CASCADE)

    def __str__(self):
        return 'City: %s' % (self.name)


class Category(BaseModel):
    """List of category"""
    name = models.CharField(max_length=255)

    def __str__(self):
        return 'Category: %s' % (self.name)


class SubCategory(BaseModel):
    """List of sub-category"""
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return 'Sub-Category: %s' % (self.name)


class Topic(BaseModel):
    """List of topic"""
    name = models.CharField(max_length=255)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE)

    def __str__(self):
        return 'Topic: %s' % (self.name)


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports using email instead of username"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_staff = models.BooleanField(default=False)
    birthday = models.DateField(default=datetime.date.today)
    is_male = models.BooleanField(default=True)
    city = models.ForeignKey(
        City, on_delete=models.SET_NULL, null=True, blank=True)
    working_id = models.CharField(max_length=255, null=True, blank=True)
    objects = UserManager()

    USERNAME_FIELD = 'email'


class Filter(BaseModel):
    """Filter"""
    name = models.CharField(max_length=255)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)

    def __str__(self):
        return 'Filter: %s' % (self.name)


class Candidate(BaseModel):
    """Candidate of the voters"""
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    city = models.ForeignKey(
        City, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return 'Candidate: %s' % (self.name)


class CandidateTopic(BaseModel):
    """Candidate-Topic"""
    name = models.CharField(max_length=255)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)

    def __str__(self):
        return 'Candidate-Topic: %s' % (self.name)


class Vote(BaseModel):
    """Vote of the voters"""
    name = models.CharField(max_length=255)
    is_vote = models.BooleanField()
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)

    def __str__(self):
        return 'Vote: %s' % (self.name)


class Favorite(BaseModel):
    """Favorite candidates"""
    name = models.CharField(max_length=255)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)

    def __str__(self):
        return 'Favorite: %s' % (self.name)

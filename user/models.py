import random

from django.db import models
from django.contrib.auth import get_user_model
import uuid
from django.contrib.auth.models import AbstractUser
from user.myusermanager import MyUserManager


class User(AbstractUser):
    username = None
    mobile = models.CharField(max_length=11, unique=True)
    otp = models.PositiveIntegerField(blank=True, null=True)
    otp_create_time = models.DateTimeField(blank=True, null=True)
    password_otp = models.PositiveIntegerField(blank=True, null=True)
    password_otp_create_time = models.DateTimeField(null=True, blank=True)


    objects = MyUserManager()

    USERNAME_FIELD = 'mobile'



    backend = 'user.mybackend.MobileBackend'

    def __str__(self):
        return self.mobile




# Create your models here.
class CustomPrimaryKeyField(models.BigAutoField):
    def get_internal_type(self):
        return 'BigIntegerField'

    def get_prep_value(self, value):
        return value


class IdentityInformation(models.Model):
    id = CustomPrimaryKeyField(primary_key=True, editable=False)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    race = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    dob = models.DateField()
    image = models.ImageField(upload_to='pet_image/', null=True, blank=True)
    chipset = models.BooleanField(editable=True, null=True)
    barren = models.BooleanField(editable=True, null=True)
    def save(self, *args, **kwargs):
        if not self.id:
            self.id = self.generate_unique_id()
        super(IdentityInformation, self).save(*args, **kwargs)

    def generate_unique_id(self):
        while True:
            #generate random 10 digit number
            unique_id = random.randint(1000000000, 9999999999)
            if not IdentityInformation.objects.filter(id=unique_id).exists():
                return unique_id




class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile_image/', default='profile_image/default_user.png')
    full_name = models.CharField(max_length=100, blank=True, null=True)
    birth = models.DateField(null=True, blank=True)



    def __str__(self):
        return self.user.mobile


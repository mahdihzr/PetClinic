from django.db import models
from user.models import IdentityInformation
import uuid


# Create your models here.
class Staff(models.Model):
    name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)


class Vaccines(models.Model):
    pet_id = models.ForeignKey(IdentityInformation, on_delete=models.CASCADE)
    type = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    date_of_injection = models.DateField()
    brand = models.CharField(max_length=100)
    next = models.DateField(blank=True, null=True)


class MedicalRecord(models.Model):
    pet_id = models.ForeignKey(IdentityInformation, on_delete=models.CASCADE)
    date = models.DateField()
    symptoms = models.CharField(max_length=1000)
    prescription = models.CharField(max_length=1000)
    vet = models.CharField(max_length=100)
    downloads = models.FileField(upload_to='pet_medical_record/', null=True, blank=True)
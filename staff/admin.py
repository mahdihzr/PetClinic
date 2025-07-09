from django.contrib import admin
from .models import Vaccines, MedicalRecord

# Register your models here.
admin.site.register(Vaccines)
admin.site.register(MedicalRecord)

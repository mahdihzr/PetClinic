from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import auth
from django.contrib import messages
from user.models import IdentityInformation
from user.helper import age_calculator
from.models import Vaccines, MedicalRecord
import datetime
import pytz
from staff.decorators import unauthenticated_user, allowed_users
from django.contrib.auth.decorators import login_required



# Create your views here.

@login_required(login_url='/signin')
@allowed_users(allowed_roles='vet')
def vaccines(request):
    if request.method == "POST":
        if 'form_1' in request.POST:
            pet_id = request.POST['pet_id']
            try:
                pet = IdentityInformation.objects.get(id=pet_id)
                pet_vaccines = Vaccines.objects.filter(pet_id=pet_id)
                pet.age = age_calculator(pet.dob)

                context = {'pet': pet, 'pet_vaccines': pet_vaccines}
                return render(request, 'vaccines.html', context)
            except IdentityInformation.DoesNotExist:
                messages.error(request, 'Pet not found')
                return render(request, 'vaccines.html')

        elif 'form_2' in request.POST:
            pet_id = request.POST['pet_id2']
            pet = IdentityInformation.objects.get(id=pet_id)
            vaccine_type = request.POST['type']
            name = request.POST['name']
            date_of_injection = request.POST['date']
            brand = request.POST['brand']
            next_vaccine = request.POST['next']
            vaccine = Vaccines.objects.create(pet_id=pet, type=vaccine_type, name=name, date_of_injection=date_of_injection, brand=brand, next=next_vaccine)
            vaccine.save()

            return redirect('/vaccines')

    else:

        return render(request, 'vaccines.html')


@login_required(login_url='/signin')
@allowed_users(allowed_roles='vet')
def medical_records(request):
    if request.method == "POST":
        if 'form_1' in request.POST:
            pet_id = request.POST['pet_id']
            try:
                pet = IdentityInformation.objects.get(id=pet_id)
                pet_records = MedicalRecord.objects.filter(pet_id=pet_id)
                pet.age = age_calculator(pet.dob)

                context = {'pet': pet, 'medical_records': pet_records}
                return render(request, 'medical_records.html', context)
            except IdentityInformation.DoesNotExist:
                messages.error(request, 'Pet not found')
                return render(request, 'medical_records.html')

        elif 'form_2' in request.POST:
            pet_id = request.POST['pet_id2']
            pet = IdentityInformation.objects.get(id=pet_id)
            date = request.POST["date"]
            symptoms = request.POST["symptoms"]
            prescription = request.POST["prescription"]
            vet = request.POST["vet"]
            if request.FILES["downloads"]:
                downloads = request.FILES["downloads"]
            else:
                downloads = None
            record = MedicalRecord.objects.create(pet_id=pet, date=date, symptoms=symptoms, prescription=prescription, vet=vet, downloads=downloads)
            record.save()

            return redirect('/medical_records')

    else:

        return render(request, 'medical_records.html')


@login_required(login_url='/signin')
@allowed_users(allowed_roles='vet')
def chipset_barren(request):
    if request.method == "POST":
        if 'form_1' in request.POST:
            pet_id = request.POST['pet_id']
            try:
                pet = IdentityInformation.objects.get(id=pet_id)
                pet.age = age_calculator(pet.dob)

                context = {'pet': pet, }
                return render(request, 'chipset_barren.html', context)
            except IdentityInformation.DoesNotExist:
                messages.error(request, 'Pet not found')
                return render(request, 'chipset_barren.html')

        elif 'form_2' in request.POST:
            pet_id = request.POST['pet_id2']
            pet = IdentityInformation.objects.get(id=pet_id)
            if 'chipset' in request.POST:
                pet_chipset = True
            else:
                pet_chipset = False

            if 'barren' in request.POST:
                pet_barren = True
            else:
                pet_barren = False

            print(pet)
            print(type(pet_chipset), pet_barren)


            pet.chipset = pet_chipset
            pet.barren = pet_barren
            pet.save()

            return redirect('/chipset_barren')

    else:

        return render(request, 'chipset_barren.html')
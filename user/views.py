from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import auth, Group
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from .models import Profile, IdentityInformation, User
from staff.models import Vaccines, MedicalRecord
from .forms import SignUpForm, SignInForm, IdentityInformationForm
from . import helper
import datetime
import pytz
from staff.decorators import unauthenticated_user, allowed_users
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode




# Create your views here.
@unauthenticated_user
def signup(request):
    if request.method == 'POST':
        # username = request.POST['username']
        mobile = request.POST['mobile']
        password = request.POST['password']
        retyped_password = request.POST['retyped_password']

        if password == retyped_password:
            if User.objects.filter(mobile=mobile).exists():
                messages.info(request, "phone number is Already Registered")
                return redirect('/signup')
            else:
                otp_create_time = datetime.datetime.now(tz=pytz.utc)
                otp = helper.get_random_otp()
                # helper.send_otp(mobile, otp)
                print(otp)

                user = User.objects.create_user(mobile=mobile, otp_create_time=otp_create_time, password=password,
                                                otp=otp, is_active=False)
                group = Group.objects.get(name='customer')
                user.groups.add(group)

                user.save()

                user_profile = Profile.objects.create(user=user)
                user_profile.save()

                request.session['user_mobile'] = mobile
                return HttpResponseRedirect(reverse('verify'))

        else:
            messages.info(request, "Passwords Does Not Match")
            return redirect('signup')

    else:
        return render(request, 'signup.html')

@unauthenticated_user
def verify(request):
    try:
        mobile = request.session.get('user_mobile')
        user = User.objects.get(mobile=mobile)

        if request.method == "POST":
            # combine otp digits
            otp1 = request.POST['otp1']
            otp2 = request.POST['otp2']
            otp3 = request.POST['otp3']
            otp4 = request.POST['otp4']
            otp = int(str(otp1)+str(otp2)+str(otp3)+str(otp4))

            # check otp expiration
            if not helper.check_otp_expiration(user.mobile):
                messages.error(request, "OTP is expired, please try again.")
                return HttpResponseRedirect(reverse('verify'))

            # check otp
            if user.otp != otp:
                messages.error(request, "OTP is incorrect.")
                return HttpResponseRedirect(reverse('verify'))

            user.is_active = True
            user.save()



            return HttpResponseRedirect(reverse('signin'))

        else:
            otp = user.otp
            remaining = helper.otp_time_remaining(mobile)
            return render(request, 'verify.html', {'mobile': mobile, 'remaining': remaining, 'otp': otp})

    except User.DoesNotExist:
        messages.error(request, "Something went wrong, try again.")
        return HttpResponseRedirect(reverse('signin'))


def resend_sms(request):
    mobile = request.POST['resend']
    user = User.objects.get(mobile=mobile)
    otp_create_time = datetime.datetime.now(tz=pytz.utc)
    otp = helper.get_random_otp()
    # helper.send_otp(mobile, otp)
    print(otp)
    user.otp_create_time = otp_create_time
    user.otp = otp
    user.save()
    request.session['user_mobile'] = mobile
    return redirect('verify')

@unauthenticated_user
def signin(request):
    if request.method == 'POST':

        mobile = request.POST['mobile']
        password = request.POST['password']

        user = auth.authenticate(mobile=mobile, password=password)
        if user:

            if user.is_active:
                auth.login(request, user)

                if user.groups.all()[0].name in ['customer']:
                    return redirect('profile')
                else:
                    return redirect('/vaccines')

            else:
                otp_create_time = datetime.datetime.now(tz=pytz.utc)
                otp = helper.get_random_otp()
                # helper.send_otp(mobile, otp)
                print(otp)
                user.otp_create_time = otp_create_time
                user.otp = otp
                user.save()
                request.session['user_mobile'] = mobile
                return redirect('verify')


        else:
            messages.info(request, "Credentials Invalid")
            return redirect('/signin')

    else:

        return render(request, 'signin.html', {})


@login_required(login_url="/signin/")
def signout(request):
    logout(request)
    return redirect('/signin/')


@unauthenticated_user
def reset_password(request):
    if request.method == 'POST':
        mobile = request.POST['mobile']
        try:
            user = User.objects.get(mobile=mobile)
            otp_create_time = datetime.datetime.now(tz=pytz.utc)
            otp = helper.get_random_otp()
            # helper.send_otp(mobile, otp)
            print(otp)
            user.password_otp_create_time = otp_create_time
            user.password_otp = otp
            user.save()
            request.session['user_mobile'] = mobile
            return redirect('verify_password')

        except User.DoesNotExist:
            messages.info(request, "User does not exist")
            return redirect('/reset_password')
    else:
        return render(request, 'reset_password.html')


class CustomPasswordResetTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            str(user.pk) + str(timestamp) +
            str(user.is_active)
        )


@unauthenticated_user
def verify_password(request):
    try:
        mobile = request.session.get('user_mobile')
        user = User.objects.get(mobile=mobile)

        if request.method == "POST":
            # combine otp digits
            otp1 = request.POST['otp1']
            otp2 = request.POST['otp2']
            otp3 = request.POST['otp3']
            otp4 = request.POST['otp4']
            otp = int(str(otp1)+str(otp2)+str(otp3)+str(otp4))

            # check otp expiration
            if not helper.check_password_otp_expiration(user.mobile):
                messages.error(request, "OTP is expired, please try again.")
                return HttpResponseRedirect(reverse('verify_password'))

            # check otp
            if user.password_otp != otp:
                messages.error(request, "OTP is incorrect.")
                return HttpResponseRedirect(reverse('verify_password'))

            password_reset_token_generator = CustomPasswordResetTokenGenerator()
            user_token = password_reset_token_generator.make_token(user)
            request.session['user_mobile'] = mobile




            return redirect(f'/change_password/{mobile}/{user_token}') ########################################################

        else:
            otp = user.password_otp
            remaining = helper.password_otp_time_remaining(mobile)
            return render(request, 'verify_password.html', {'mobile': mobile, 'remaining': remaining, 'otp': otp})

    except User.DoesNotExist:
        messages.error(request, "Something went wrong, try again.")
        return HttpResponseRedirect(reverse('reset_password'))



def change_password(request, mobile, token):
    user = User.objects.get(mobile=mobile)

    if CustomPasswordResetTokenGenerator().check_token(user, token):
        # Token is valid, allow user to reset password
        if request.method == 'POST':
            # Handle password reset form submission
            password = request.POST['password']
            retyped_password = request.POST['retyped_password']

            if password == retyped_password:
                # Update user's password
                user.set_password(password)
                user.save()
            else:
                messages.info(request, "Passwords Does Not Match")
                return redirect(request.path_info)
            return redirect('/signin')
        else:
            return render(request, 'change_password.html', {'mobile': mobile})
    else:
        # Token is invalid or expired
        return redirect('/reset_password')



@login_required(login_url="/signin/")
@allowed_users(allowed_roles='customer')
def profile(request):
    if request.method == "POST":
        mobile = request.user.mobile
        owner = User.objects.get(mobile=mobile)

        if 'form_one' in request.POST:
            try:
                profile_image = request.FILES['profile_image']
                user_name = request.POST['user_name']
                user_birth = request.POST['user_birth']

                profile_object = Profile.objects.get(user=owner)
                profile_object.image = profile_image
                profile_object.full_name = user_name
                profile_object.birth = user_birth
                profile_object.save()

                return redirect('/profile')

            except:
                user_name = request.POST['user_name']
                user_birth = request.POST['user_birth']

                profile_object = Profile.objects.get(user=owner)
                profile_object.full_name = user_name
                profile_object.birth = user_birth

                profile_object.save()

                return redirect('/profile')


        elif 'form_two' in request.POST:

            pet_name = request.POST['pet_name']
            pet_race = request.POST['pet_race']
            pet_dob = request.POST['pet_dob']
            pet_type = request.POST['pet_type']
            pet_image = request.FILES['pet_image']
            if 'chipset' in request.POST:
                pet_chipset = True
            else:
                pet_chipset = False

            if 'barren' in request.POST:
                pet_barren = True
            else:
                pet_barren = False




            new_pet = IdentityInformation.objects.create(name=pet_name, race=pet_race, dob=pet_dob, type=pet_type,
                                                         image=pet_image, owner=owner, chipset=pet_chipset, barren=pet_barren)
            new_pet.save()
            return redirect('/profile')

        elif 'delete_pet' in request.POST:
            pet_id = request.POST['delete_pet']
            pet = IdentityInformation.objects.get(id=pet_id)
            pet.delete()
            return redirect('/profile')





    else:
        user_model = request.user
        profile_model = Profile.objects.get(user=user_model)
        try:
            pets = IdentityInformation.objects.filter(owner=user_model)

            context = {'profile': profile_model, 'pets': pets}
            return render(request, 'profile.html', context)

        except:
            context = {'profile': profile_model}
            return render(request, 'profile.html', context)


@login_required(login_url="/signin/")
@allowed_users(allowed_roles='customer')
def home(request):
    user_model = request.user
    profile_model = Profile.objects.get(user=user_model)
    try:
        pets = IdentityInformation.objects.filter(owner=user_model)

        for pet in pets:
            pet.age = helper.age_calculator(pet.dob)
            pet.vaccines = Vaccines.objects.filter(pet_id=pet)
            pet.medical_records = MedicalRecord.objects.filter(pet_id=pet)



        context = {'profile': profile_model, 'pets': pets}
        return render(request, 'home.html', context)

    except:
        context = {'profile': profile_model}
        return render(request, 'home.html', context)






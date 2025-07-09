from kavenegar import *
#from shop.settings import Kavenegar_API
from random import randint
from . import models
import datetime, pytz


Kavenegar_API = "*****************************"

def send_otp(mobile, otp):
    mobile = [mobile, ]
    try:
        api = KavenegarAPI(Kavenegar_API)
        params = {
            'sender': '1000596446',  # optional
            'receptor': mobile,  # multiple mobile number, split by comma
            'message': 'Your OTP is {}'.format(otp),
        }
        response = api.sms_send(params)
        print('OTP: ', otp)
        print(response)
    except APIException as e:
        print(e)
    except HTTPException as e:
        print(e)




def get_random_otp():
    return randint(1000, 9999)


def check_otp_expiration(mobile):
    try:
        user = models.User.objects.get(mobile=mobile)
        now = datetime.datetime.now(pytz.utc)
        otp_time = user.otp_create_time
        diff_time = now - otp_time
        print('OTP TIME: ', otp_time)
        print('now TIME: ', now)

        print('OTP TIME: ', diff_time)

        if diff_time.seconds > 120:
            return False
        return True

    except models.User.DoesNotExist:
        return False


def check_password_otp_expiration(mobile):
    try:
        user = models.User.objects.get(mobile=mobile)
        now = datetime.datetime.now(pytz.utc)
        otp_time = user.password_otp_create_time
        diff_time = now - otp_time
        print('OTP TIME: ', otp_time)
        print('now TIME: ', now)

        print('OTP TIME: ', diff_time)

        if diff_time.seconds > 120:
            return False
        return True

    except models.User.DoesNotExist:
        return False


def otp_time_remaining(mobile):
    try:
        user = models.User.objects.get(mobile=mobile)
        now = datetime.datetime.now(pytz.utc)
        otp_time = user.otp_create_time

        remaining = otp_time.timestamp() - now.timestamp() + 120
        remaining = remaining // 1


        return remaining

    except models.User.DoesNotExist:
        return False


def password_otp_time_remaining(mobile):
    try:
        user = models.User.objects.get(mobile=mobile)
        now = datetime.datetime.now(pytz.utc)
        otp_time = user.password_otp_create_time

        remaining = otp_time.timestamp() - now.timestamp() + 120
        remaining = remaining // 1


        return remaining

    except models.User.DoesNotExist:
        return False

def age_calculator(birth):
    now = datetime.date.today()
    diff = now - birth
    diff = diff.days

    years = diff // 365
    months = (diff % 365) // 30
    days = (diff % 365) % 30

    if years:
        age = str(years) + " Years " + str(months) + " Months " + str(days) + " Days"
    else:
        if months:
            age = str(months) + " Months " + str(days) + " Days"
        else:
            age = str(days) + " Days"

    return age


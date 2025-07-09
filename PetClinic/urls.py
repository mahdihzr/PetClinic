"""
URL configuration for PetClinic project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from user.views import signup, verify, signin, profile, home, signout, resend_sms, reset_password, verify_password,change_password
from staff.views import vaccines, medical_records, chipset_barren
from shop.views import shop_admin, shop_admin_category, shop_admin_create_product, shop_admin_manage_product,\
    shop_admin_edit_product, product_list, product_detail, cart, order, bank_token_generator, bank_page, payment_result, \
    bank_confirmation


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', signin, name='index'),
    path('signup/', signup, name='signup'),
    path('verify/', verify, name='verify'),
    path('resend_sms/', resend_sms, name='resend_sms'),
    path('signin/', signin, name='signin'),
    path('profile/', profile, name='profile'),
    path('home/', home, name='home'),
    path('vaccines/', vaccines, name='vaccines'),
    path('medical_records/', medical_records, name='medical_records'),
    path('chipset_barren/', chipset_barren, name='chipset_barren'),
    path('signout/', signout, name='signout'),
    path('reset_password/', reset_password, name='reset_password'),
    path('verify_password/', verify_password, name='verify_password'),
    path('change_password/<mobile>/<token>/', change_password, name='change_password'),
    path('shop/admin/', shop_admin, name='shop_admin'),
    path('shop/admin/category/', shop_admin_category, name='shop_admin_category'),
    path('shop/admin/create_product/', shop_admin_create_product, name='shop_admin_create_product'),
    path('shop/admin/manage_product/', shop_admin_manage_product, name='shop_admin_manage_product'),
    path('shop/admin/edit_product/<pk>', shop_admin_edit_product, name='shop_admin_edit_product'),
    path('shop/product_list/', product_list, name='product_list'),
    path('shop/product_detail/<pk>', product_detail, name='product_detail'),
    path('shop/cart', cart, name='cart'),
    path('shop/order_summary', order, name='order'),
    path('shop/bank_token_generator', bank_token_generator, name='bank_token_generator'),
    path('shop/bank_page/<pk>', bank_page, name='bank_page'),
    path('shop/payment_result', payment_result, name='payment_result'),
    path('shop/bank_confirmation', bank_confirmation, name='bank_confirmation'),


    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

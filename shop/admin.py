from django.contrib import admin
from .models import Category, Product, Image, Vote, Comment, ProductInfo, Cart, Address, Order, BankPayment,\
    BankCustomer, OrderItem, StockReservation, Transaction


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    list_filter = ('parent',)


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price')
    list_filter = ('category',)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Image)
admin.site.register(Vote)
admin.site.register(Comment)
admin.site.register(ProductInfo)
admin.site.register(Cart)
admin.site.register(Address)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(BankPayment)
admin.site.register(BankCustomer)
admin.site.register(StockReservation)
admin.site.register(Transaction)


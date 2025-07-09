from datetime import datetime
from django.utils import timezone
from datetime import timedelta
from django.utils.timezone import now
import uuid


import pytz
from django.utils.timezone import is_aware, make_aware
from django.db import models
from user.models import User


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='subcategories')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

    def get_full_path(self):
        """Returns the full category hierarchy as a list."""
        path = []
        current = self
        while current is not None:
            path.append(current.name)
            current = current.parent
        return path[::-1]


class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    in_stock = models.IntegerField(default=1)
    animal = models.CharField(max_length=100)
    good_for = models.CharField(max_length=100, blank=True, null=True)
    brand = models.CharField(max_length=100)
    created_at = models.DateField(default=now)
    sales = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def get_gallery(self):
        return Image.objects.filter(product=self)

    def score_counter(self):
        """Calculate average score from votes."""
        votes = Vote.objects.filter(product=self)
        if votes.exists():
            total_score = sum(vote.vote for vote in votes)
            return total_score / len(votes)
        return 0

    def total_reviews(self):
        votes = Vote.objects.filter(product=self)
        if votes.exists():
            return len(votes)
        else:
            return 0


class ProductInfo(models.Model):
    product = models.ForeignKey(Product, related_name="product_infos", on_delete=models.CASCADE)
    key = models.CharField(max_length=100)
    value = models.CharField(max_length=100)


class Image(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)

    def __str__(self):
        return f"Image for {self.product.name}"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()
    created_at = models.DateTimeField(default=datetime.now())

    def time_elapsed(self):
        now = datetime.now(pytz.utc)  # Ensure 'now' is timezone-aware
        past_time = self.created_at
        if not is_aware(past_time):  # Convert to timezone-aware if naive
            past_time = make_aware(past_time, pytz.utc)

        delta = now - past_time

        minutes = delta.total_seconds() / 60
        hours = minutes / 60
        days = hours / 24
        weeks = days / 7
        months = days / 30.44  # Approximate month length
        years = days / 365.25  # Account for leap years

        if minutes < 60:
            return f"{int(minutes)} minute(s) ago"
        elif hours < 24:
            return f"{int(hours)} hour(s) ago"
        elif days < 7:
            return f"{int(days)} day(s) ago"
        elif weeks < 4:
            return f"{int(weeks)} week(s) ago"
        elif months < 12:
            return f"{int(months)} month(s) ago"
        else:
            year_part = int(years)
            month_part = int((years - year_part) * 12)
            return f"{year_part} year(s) and {month_part} month(s) ago"


    def __str__(self):
        return f"Comment for {self.product.name}"


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='votes')
    vote = models.IntegerField()

    def __str__(self):
        return f"Vote for {self.product.name}"


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def get_total_price(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.name} ({self.user})"


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.address} for ({self.user})"



def two_days_later():
    return timezone.localdate() + timedelta(days=2)


class Order(models.Model):
    STATUS_CHOICES = [

        ('payment', 'payment'),
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='payment')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True, blank=True)
    delivery_date = models.DateField(default=two_days_later())
    customer_name = models.CharField(max_length=100, blank=True, null=True)

    def calculate_total(self):
        total = sum(item.get_total_price() for item in self.items.all())
        self.total_price = total
        self.save()
        return total

    def __str__(self):
        return f"Order {self.id} - {self.user.username} ({self.status})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def get_total_price(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order {self.order.id})"




class StockReservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    expires_at = models.DateTimeField()


#for fake bank page
class BankCustomer(models.Model):
    customer_name = models.CharField(max_length=255)
    customer_uuid = models.UUIDField(default=uuid.uuid4)


#for fake bank page
class BankPayment(models.Model):
    trans_id = models.UUIDField(default=uuid.uuid4)
    order_id = models.IntegerField()
    amount = models.FloatField()
    call_back_url = models.URLField()
    time = models.DateTimeField(default=datetime.now)
    status = models.IntegerField(default=-1)


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=True, null=True)
    trans_id = models.UUIDField(default=uuid.uuid4)
    amount = models.FloatField()
    status = models.IntegerField(default=-1)

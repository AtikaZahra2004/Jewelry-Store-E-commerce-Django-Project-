from django.db import models

from django.contrib.auth.models import User

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    front_image = models.ImageField(upload_to='products/')
    back_image = models.ImageField(upload_to='products/', blank=True, null=True)

    discount = models.IntegerField(default=0)   # ex: 32%
    is_sold_out = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

from django.db import models
from django.contrib.auth.models import User


class Order(models.Model):

    PAYMENT_CHOICES = (
        ("cod", "Cash on Delivery"),
        ("razorpay", "Razorpay"),
        ("paypal", "PayPal"),
    )

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)

    notes = models.TextField(blank=True, null=True)

    payment_method = models.CharField(
        max_length=50,
        choices=PAYMENT_CHOICES,
        default="cod"
    )

    total_amount = models.FloatField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product_name = models.CharField(max_length=200)
    price = models.FloatField()
    quantity = models.IntegerField()

    def __str__(self):
        return self.product_name



    


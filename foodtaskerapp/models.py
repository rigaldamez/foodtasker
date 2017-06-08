from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# Create your models here.

class Restaurant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='restaurant') #specifies the owner of the restaurant note: 1-2-1 relationship, deletes
    name = models.CharField(max_length=500)
    phone = models.CharField(max_length=500)
    address = models.CharField(max_length=500)
    logo = models.ImageField(upload_to='restaurant/logo', blank=False)

    #to reference the object model by its name in the dashboard.
    def __str__(self):
        return self.name

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer') #specifies the owner of the restaurant note: 1-2-1 relationship, deletes
    avatar = models.CharField(max_length=500)
    phone = models.CharField(max_length=500, blank=True)
    address = models.CharField(max_length=500, blank=True)

    #to reference the object model by its name in the dashboard.
    def __str__(self):
        return self.user.get_full_name()

class Driver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='driver') #specifies the owner of the restaurant note: 1-2-1 relationship, deletes
    avatar = models.CharField(max_length=500)
    phone = models.CharField(max_length=500, blank=True)
    address = models.CharField(max_length=500, blank=True)

    #to reference the object model by its name in the dashboard.
    def __str__(self):
        return self.user.get_full_name()

class Meal(models.Model):
    restaurant = models.ForeignKey(Restaurant) #link back to the Restaurant this Meal belongs to
    name = models.CharField(max_length=500)
    short_description = models.CharField(max_length=500)
    image = models.ImageField(upload_to='meal_images/', blank=False)
    price = models.IntegerField(default=0)

    def __str__(self):
         return self.name

class Order(models.Model):
    COOKING = 1
    READY = 2
    ONTHEWAY = 3
    DELIVERED = 4

    STATUS_CHOICES = (
        (COOKING, 'Cooking'),
        (READY, 'Ready'),
        (ONTHEWAY, 'On its way'),
        (DELIVERED, 'Delivered')
    )

    customer = models.ForeignKey(Customer) #link to the Customer that placed the order
    restaurant = models.ForeignKey(Restaurant) #link to the Restaurant
    driver = models.ForeignKey(Driver, blank = True, null = True) #link to the Driver doing the delivery
    address = models.CharField(max_length=500)
    total = models.IntegerField()
    status = models.IntegerField(choices = STATUS_CHOICES)
    created_at = models.DateTimeField(default = timezone.now)
    picked_at = models.DateTimeField(blank = True, null = True)

    def __str__(self):
         return str(self.id)

class OrderDetails(models.Model):
    order = models.ForeignKey(Order, related_name = 'order_details')
    meal = models.ForeignKey(Meal)
    quantity = models.IntegerField()
    sub_total = models.IntegerField()

    def __str__(self):
         return str(self.id)

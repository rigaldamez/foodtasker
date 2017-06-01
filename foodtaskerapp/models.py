from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Restaurant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='restaurant') #specifies the owner of the restaurant note: 1-2-1 relationship, deletes
    name = models.CharField(max_length=500)
    phone = models.CharField(max_length=500)
    address = models.CharField(max_length=500)
    logo = models.ImageField(upload_to='restaurant/logo', blank=False)

    #to reference the objecy by its name.
    def __str__(self):
        return self.name

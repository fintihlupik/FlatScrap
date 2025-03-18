from django.db import models

class Property(models.Model):  
    price = models.CharField(max_length=50) 
    location = models.CharField(max_length=200)  
    surface = models.CharField(max_length=20) 
    url = models.URLField(unique=True)
    type = models.CharField(max_length=50)
    agency = models.CharField(max_length=50)
    first_seen = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)  
    is_active = models.BooleanField(default=True)
     
    

    def __str__(self):
        return self.title #pensar en devolver algo más util


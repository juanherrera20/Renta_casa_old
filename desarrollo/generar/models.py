from django.db import models
from django.db.models.fields import CharField, URLField
from django.db.models.fields.files import ImageField

class p(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    descrip = models.CharField(max_length = 250)
    image = models.ImageField(upload_to="Imagenes/images")
    url = URLField(blank =True)
# Create your models here.

from unittest.util import _MAX_LENGTH
from django.db import models

# Create your models here.


class Tokenlist(models.Model):
    token = models.CharField(max_length=100)
    time = models.DecimalField(max_digits=20,decimal_places=9)

# class Board(models.Model):
#     board=models.TextField(max_length=2000000)
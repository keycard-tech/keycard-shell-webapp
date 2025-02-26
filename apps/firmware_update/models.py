from django.db import models

# Create your models here.

class Firmware(models.Model):
  version = models.CharField(max_length=10, unique=True, default="1.0.0")

  def __str__(self):
        return f"{self.version}"

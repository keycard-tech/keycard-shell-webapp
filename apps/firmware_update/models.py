from django.db import models
class Firmware(models.Model):
  version = models.CharField(max_length=10, unique=True, default="1.0.0")
  creation_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

  def __str__(self):
    return f"{self.version}"

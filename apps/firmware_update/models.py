from django.db import models
class Firmware(models.Model):
  version = models.CharField(max_length=10, unique=True, default="0.0.1", verbose_name="Firmware version")
  creation_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
  fw_hash = models.CharField(max_length=64, null=True, blank=True, unique=True, default=None, verbose_name="Firmware hash")

  def __str__(self):
    return f"{self.version}"

from django.db import models

class DB(models.Model):
  class Meta:
    verbose_name_plural = "DB"

  erc20_url = models.CharField(max_length=2000, null=True, blank=True)
  chain_url = models.CharField(max_length=2000, null=True, blank=True)
  abi_url = models.CharField(max_length=2000, null=True, blank=True)
  version = models.CharField(max_length=12)
  creation_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
  db_hash = models.CharField(max_length=64, null=True, blank=True, unique=True, default=None)

  def __str__(self):
    return f"{self.erc20_url}, {self.chain_url}, {self.abi_url}, {self.version}"

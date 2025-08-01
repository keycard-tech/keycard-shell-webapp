from django.db import models

class DB(models.Model):
  class Meta:
    verbose_name_plural = "Database"

  erc20_url = models.CharField(max_length=2000, null=True, blank=True, verbose_name="Tokens URL")
  chain_url = models.CharField(max_length=2000, null=True, blank=True, verbose_name="Chains URL")
  abi_url = models.CharField(max_length=2000, null=True, blank=True, verbose_name="ABI URL")
  version = models.CharField(max_length=12, verbose_name="DB version")
  creation_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
  db_hash = models.CharField(max_length=64, null=True, blank=True, unique=True, default=None)
  full_db_hash = models.CharField(max_length=64, null=True, blank=True, unique=True, default=None, verbose_name="DB hash")

  def __str__(self):
    return f"{self.version}"

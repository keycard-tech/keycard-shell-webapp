from django.shortcuts import render

from apps.device_verify.models import Device

def index(request):
  print(Device.objects.all())
  return render(request, 'keycard_shell/device_verify.html', context=None)

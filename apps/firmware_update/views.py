import json
from django.http import HttpResponse
from django.shortcuts import render
from .models import Firmware

# Create your views here.
def fw_context(request):
  fw = Firmware.objects.last()

  fw_context = {
    "fw_path": fw.version + '/firmware.bin',
    "changelog_path": fw.version + '/changelog.md',
    "version": fw.version
    }

  return HttpResponse(json.dumps(fw_context), content_type='application/json')


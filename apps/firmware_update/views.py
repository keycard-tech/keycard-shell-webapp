import json
from django.http import HttpResponse
from django.shortcuts import render
from .models import Firmware

# Create your views here.

def index(request):
  return render(request, 'keycard_shell/fw_release_notes.html')

def fw_context(request):
  fw = Firmware.objects.last()

  fw_context = {
    "fw_path": fw.version + '/firmware.bin',
    "version": fw.version
    }

  return HttpResponse(json.dumps(fw_context), content_type='application/json')


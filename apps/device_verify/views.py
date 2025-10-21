from django.shortcuts import render
from django.http import HttpResponse

from common.device_verification import verify

import json

def index(request):
  return render(request, 'keycard_shell/device_verify.html', context=None)

def verify_device(request):
  if request.method == 'POST':
    device_data = {}
    device_data["device_id"] = request.POST.get('device_id')
    device_data["challenge"] = request.POST.get('challenge')
    device_data["signature"] = request.POST.get('signature')
    device_data["initial_challenge"] = request.POST.get('initial_challenge')
    
    resp = verify(device_data)

    return HttpResponse(json.dumps(resp), content_type='application/json')


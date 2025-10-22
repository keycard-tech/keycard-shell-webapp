from django.shortcuts import render
from django.http import HttpResponse

from .models import Campaign
from common.device_verification import verify

import json

def index(request, campaign_name, redeem_code):
  context = {}
  context["campaign_name"] = campaign_name
  context["redeem_code"] = redeem_code  
  
  try:
    r_code = Campaign.objects.filter(campaign_name=campaign_name, redemption_state=False).get(redeem_code=redeem_code)
    context["redeem_code_valid"] = True
    context["address_type"] = r_code.redemption_address_type
  except Exception as err:
    context["redeem_code_valid"] = False  
  
  return render(request, 'keycard_shell/redeem.html', context)

def redeem(request):
  if request.method == 'POST':
    device_data = {}
    device_data["device_id"] = request.POST.get('device_id')
    device_data["challenge"] = request.POST.get('challenge')
    device_data["signature"] = request.POST.get('signature')
    device_data["initial_challenge"] = request.POST.get('initial_challenge')
    
    redeem_data = {}
    redeem_data["campaign_name"] = request.POST.get('campaign_name')
    redeem_data["redeem_code"] = request.POST.get('redeem_code')
    redeem_data["redemption_address"] = request.POST.get('redemption_address')
    
    resp = verify(device_data, redeem_data)

    return HttpResponse(json.dumps(resp), content_type='application/json')

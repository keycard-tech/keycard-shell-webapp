import json
from django.shortcuts import render
from .models import DB
from django.views.decorators.http import require_GET
from django.http import HttpResponse
from common.utils import iter_query

def index(request):
  return render(request, 'keycard_shell/shell_update.html')

def release_notes(request):
  return render(request, 'keycard_shell/db_version_history.html')

def db_context(request):
  db = DB.objects.last()

  context = {
    "db_path": db.version + '/db.bin',
    "version": db.version
  }

  return HttpResponse(json.dumps(context), content_type='application/json')


def dbs_context(request):
  dbs = DB.objects.all()
  
  data = []
  
  for db in dbs:
    context = {
      "db_path": db.version + '/db.bin',
      "version": db.version,
      "creation_date": db.creation_date.strftime('%Y-%m-%d %H:%M'),
      "token_link": db.erc20_url,
      "chain_link": db.chain_url,
      "abi_link": db.abi_url 
    }
    
    data.append(context)
    
    return HttpResponse(json.dumps(data), content_type='application/json')
  
  

@require_GET
def security_txt(request):
    lines = [
        "HzV4pDh6R9Y1YE7cQL_I7vGzKj9oVdyeF5qgxWCjDZM.J9bqa4tLDBisdE_rBySdA0b3XcIl0PLE38PWQoPIwiA",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")

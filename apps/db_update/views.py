import json
from django.shortcuts import render
from .models import DB
from django.views.decorators.http import require_GET
from django.http import HttpResponse
from common.utils import iter_query

DELTA_DBS = 500

def index(request):
  return render(request, 'keycard_shell/db.html')

def db_context(request):
  db = DB.objects.last()
  dbs_query = DB.objects.all().order_by('-version')[1:DELTA_DBS]
  available_dbs = iter_query(dbs_query, "version")

  context = {
    "db_path": db.version + '/db.bin',
    "version": db.version,
    "available_db_versions": available_dbs
  }

  return HttpResponse(json.dumps(context), content_type='application/json')

@require_GET
def security_txt(request):
    lines = [
        "HzV4pDh6R9Y1YE7cQL_I7vGzKj9oVdyeF5qgxWCjDZM.J9bqa4tLDBisdE_rBySdA0b3XcIl0PLE38PWQoPIwiA",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")

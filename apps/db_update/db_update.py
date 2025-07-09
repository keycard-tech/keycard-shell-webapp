import itertools
import json
from urllib.error import HTTPError
from apps.db_update.shell_db import generate_token_bin_file
from common.errors import InvalidJSONFileError
from common.utils import makedirs, deletedirs, zip_db_files
from django.conf import settings
from urllib.request import urlopen, Request
from pathlib import Path

def upload_db_file(r_path, w_path):
  try:
    req = Request(r_path, data=None, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'})
    resp = urlopen(req)
    data = json.loads(resp.read())
    with open(w_path, "w") as outfile:
      json.dump(data, outfile)
  except json.JSONDecodeError as err:  
    raise InvalidJSONFileError(r_path)
  except HTTPError as err:
    raise err
class DBUpdate:
  element_id = itertools.count()

  def __init__(self, erc20_url, chain_url, abi_url, db_version):
    self.id = next(self.element_id)
    self.erc20_url = str(erc20_url)
    self.chain_url = str(chain_url)
    self.abi_url = str(abi_url)
    self.db_version = str(db_version)


  def upload_db(self):
    try: 
      p = settings.MEDIA_ROOT + '/' + self.db_version
      makedirs(p)

      erc20_out_path = p + '/erc20.json'
      chain_out_path = p + '/chain.json'
      abi_out_path = p + '/abi.json'
      bin_output = p + '/db.bin'
      zip_path = p + '/' + self.db_version + '.zip'

      upload_db_file(self.erc20_url, erc20_out_path)
      upload_db_file(self.chain_url, chain_out_path)
      upload_db_file(self.abi_url, abi_out_path)
      file_hash = generate_token_bin_file(erc20_out_path, chain_out_path, abi_out_path, bin_output, int(self.db_version))
      zip_db_files(Path(p), Path(zip_path))
      return file_hash
    except Exception as err: 
      deletedirs(p) 
      raise err
    
      
  def delete_db(db_version):
    p = settings.MEDIA_ROOT + '/' + db_version
    deletedirs(p)

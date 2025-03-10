import itertools
import json
from common.errors import InvalidJSONFileError
from common.utils import makedirs, deletedirs, zip_db_files
from django.conf import settings
from .token_db import generate_token_bin_file
from .db_delta import generate_db_deltas
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

class DBUpdate:
  element_id = itertools.count()

  def __init__(self, erc20_url, chain_url, db_version, prev_dbs):
    self.id = next(self.element_id)
    self.erc20_url = str(erc20_url)
    self.chain_url = str(chain_url)
    self.db_version = str(db_version)
    self.dbs = prev_dbs

  def upload_db(self):
    p = settings.MEDIA_ROOT + '/' + self.db_version
    makedirs(p)

    delta_out_path = p + '/deltas'
    makedirs(delta_out_path)

    erc20_out_path = p + '/erc20.json'
    chain_out_path = p + '/chain.json'
    bin_output = p + '/db.bin'
    zip_path = p + '/' + self.db_version + '.zip'

    upload_db_file(self.erc20_url, erc20_out_path)
    upload_db_file(self.chain_url, chain_out_path)
    file_hash = generate_token_bin_file(erc20_out_path, chain_out_path, bin_output, int(self.db_version))
    generate_db_deltas(self.db_version, self.dbs, delta_out_path)
    zip_db_files(Path(p), Path(zip_path))

    return file_hash

  def delete_db(db_version):
    p = settings.MEDIA_ROOT + '/' + db_version
    deletedirs(p)

import hashlib
import struct

from common.errors import CompareDeltasError, InvalidBinFileError, SerializeDeltaError
from common.utils import sign
from django.conf import settings

DELTA_MAGIC = 0x444c
CHAIN_MAGIC = 0x4348
ERC20_MAGIC = 0x3020
VERSION_MAGIC = 0x4532

def decode_entry(entry, magic, dec_obj):
  if(magic == CHAIN_MAGIC):
    id = struct.unpack('<I', entry[4:8])[0]
    dec_obj["chains"][id] = entry
  elif(magic == ERC20_MAGIC):
    addresses_len = struct.unpack('<B', entry[4:5])[0] * 24
    id = entry[addresses_len + 6:len(entry) - 1].decode("ascii")
    dec_obj["tokens"][id] = entry
  else:
    raise Exception(f"Error decoding .bin file.")  
    
def read_bin(f_path):
  try:
    with open(f_path, 'rb') as f:
      i = 8
      db = f.read()
      parsed = {"version": db[0:i], "chains": {}, "tokens": {}}
      print(parsed)
      while i < len(db) - 64:
        el_header = struct.unpack('<HH', db[i:i+4])
        el_length = el_header[1]
        el_magic = el_header[0]
        decode_entry(db[i:i+el_length+4], el_magic, parsed)
        i = i + el_length + 4
      return parsed
  except Exception as err:
    raise InvalidBinFileError(f_path)

def compare_db_objs(obj1, obj2, rmw, upd):
  for obj1_id in obj1:
    if(obj1_id not in obj2):
      rmw.append(obj1_id)
    else:
      if(obj1[obj1_id] != obj2[obj1_id]):
        upd[obj1_id] = obj2[obj1_id]
        rmw.append(obj1_id)

      for obj2_id in obj2:
        if(obj2_id not in obj1):
          upd[obj2_id] = obj2[obj2_id]

def compare_dbs(prev_db, latest_db):
  try:
    removed_elements = {"chains": [], "tokens": []}
    updated_elements = {"chains": {}, "tokens": {}}

    compare_db_objs(prev_db["chains"], latest_db["chains"], removed_elements["chains"], updated_elements["chains"])
    compare_db_objs(prev_db["tokens"], latest_db["tokens"], removed_elements["tokens"], updated_elements["tokens"])

    return {"removed": removed_elements, "updated": updated_elements, "latest_version": latest_db["version"]}
  except Exception as err:
    raise CompareDeltasError(prev_db["version"], latest_db["version"])

def serialize_delta(f, m, delta, delta_db_ver):
  try:
    buf = struct.pack("<HI", DELTA_MAGIC, delta_db_ver)
    chains_rmv_l = len(delta["removed"]["chains"]) * 4
    tokens_rmv_l = sum((len(i) + 1) for i in delta["removed"]["tokens"])
    buf = buf + struct.pack('<HH', chains_rmv_l, tokens_rmv_l)

    for chain_id in delta["removed"]["chains"]:
      buf = buf + struct.pack('<I', chain_id)

    for token_id in delta["removed"]["tokens"]:
      buf = buf + \
        bytes(token_id, "ascii") + b'\0'

    buf = buf + delta["latest_version"]

    for chain_upd in delta["updated"]["chains"]:
      buf = buf + chain_upd

    for token_upd in delta["updated"]["tokens"]:
      buf = buf + delta["updated"]["tokens"][token_upd]

    f.write(buf)
    m.update(buf)
  except Exception as err:
    raise SerializeDeltaError(f"Unable to create {delta_db_ver} delta")

def generate_db_delta(output, delta, delta_db_ver, m):
  with open(output, 'wb') as f:
    serialize_delta(f, m, delta, delta_db_ver)
    m_hash = m.digest()
    signature = sign(m_hash)
    f.write(signature)

def generate_db_deltas(db_version, prev_dbs, out_path):
  latest_db_path = settings.MEDIA_ROOT + '/' + db_version + '/db.bin'
  latest_db = read_bin(latest_db_path)

  for db_ver in prev_dbs:
    prev_db_path = settings.MEDIA_ROOT + '/' + db_ver + '/db.bin'
    prev_db = read_bin(prev_db_path)
    m = hashlib.sha256()
    out_p = out_path + '/delta-' + db_version + '-' + db_ver + '.bin'
    delta_obj = compare_dbs(prev_db, latest_db)
    generate_db_delta(out_p, delta_obj, int(db_ver), m)

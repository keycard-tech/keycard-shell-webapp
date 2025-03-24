import hashlib
import struct

from common.consts import CHAIN_MAGIC, DELTA_MAGIC, ERC20_MAGIC
from common.errors import CompareDeltasError, DecodeEntryError, InvalidBinFileError, SerializeDeltaError
from common.utils import sign
from django.conf import settings



def decode_entry(entry, magic, parsed_db):
  if(magic == CHAIN_MAGIC):
    id = struct.unpack('<I', entry[4:8])[0]
    parsed_db["chains"][id] = entry
  elif(magic == ERC20_MAGIC):
    addresses_len = struct.unpack('<B', entry[4:5])[0] * 24
    id = entry[addresses_len + 6:len(entry) - 1].decode("ascii")
    parsed_db["tokens"][id] = entry
  else:
    raise DecodeEntryError
    
def read_bin(f_path):
  try:
    with open(f_path, 'rb') as f:
      i = 8
      db = f.read()
      parsed_db = {"version": db[0:i], "chains": {}, "tokens": {}}
      while i < len(db) - 64:
        entry_header = struct.unpack('<HH', db[i:i+4])
        entry_length = entry_header[1]
        entry_magic = entry_header[0]
        decode_entry(db[i:i+entry_length+4], entry_magic, parsed_db)
        i = i + entry_length + 4
      return parsed_db
  except Exception:
    raise InvalidBinFileError(f_path)

def compare_db_objs(prev_db_entries, latest_db_entries, removed_entries, updated_entries):
  for prev_db_entry in prev_db_entries:
    if(prev_db_entry not in latest_db_entries):
      removed_entries.append(prev_db_entry)
    else:
      if(prev_db_entries[prev_db_entry] != latest_db_entries[prev_db_entry]):
        updated_entries[prev_db_entry] = latest_db_entries[prev_db_entry]
        removed_entries.append(prev_db_entry)

      for latest_db_entry in latest_db_entries:
        if(latest_db_entry not in prev_db_entries):
          updated_entries[latest_db_entry] = latest_db_entries[latest_db_entry]

def compare_dbs(prev_db, latest_db):
  try:
    removed_entries = {"chains": [], "tokens": []}
    updated_entries = {"chains": {}, "tokens": {}}

    compare_db_objs(prev_db["chains"], latest_db["chains"], removed_entries["chains"], updated_entries["chains"])
    compare_db_objs(prev_db["tokens"], latest_db["tokens"], removed_entries["tokens"], updated_entries["tokens"])

    return {"removed": removed_entries, "updated": updated_entries, "latest_version": latest_db["version"]}
  except Exception as err:
    raise CompareDeltasError(prev_db["version"], latest_db["version"])

def serialize_delta(f, m, delta, delta_db_ver):
  try:
    delta_buffer = struct.pack("<HI", DELTA_MAGIC, delta_db_ver)
    chains_rmv_l = len(delta["removed"]["chains"]) * 4
    tokens_rmv_l = sum((len(i) + 1) for i in delta["removed"]["tokens"])
    delta_buffer = delta_buffer + struct.pack('<HH', chains_rmv_l, tokens_rmv_l)

    for chain_id in delta["removed"]["chains"]:
      delta_buffer = delta_buffer + struct.pack('<I', chain_id)

    for token_id in delta["removed"]["tokens"]:
      delta_buffer = delta_buffer + \
        bytes(token_id, "ascii") + b'\0'

    delta_buffer = delta_buffer + delta["latest_version"]

    for chain_upd in delta["updated"]["chains"]:
      delta_buffer = delta_buffer + chain_upd

    for token_upd in delta["updated"]["tokens"]:
      delta_buffer = delta_buffer + delta["updated"]["tokens"][token_upd]

    f.write(delta_buffer)
    m.update(delta_buffer)
  except Exception as err:
    raise SerializeDeltaError(delta_db_ver)

def generate_db_delta(output, delta, delta_db_ver, m):
  with open(output, 'wb') as f:
    serialize_delta(f, m, delta, delta_db_ver)
    m_hash = m.digest()
    signature = sign(m_hash)
    f.write(signature)

def generate_db_deltas(current_db_ver, prev_dbs, out_path):
  latest_db_path = settings.MEDIA_ROOT + '/' + current_db_ver + '/db.bin'
  latest_db = read_bin(latest_db_path)

  for prev_db_ver in prev_dbs:
    prev_db_path = settings.MEDIA_ROOT + '/' + prev_db_ver + '/db.bin'
    prev_db = read_bin(prev_db_path)
    m = hashlib.sha256()
    out_p = out_path + '/delta-' + current_db_ver + '-' + prev_db_ver + '.bin'
    delta_obj = compare_dbs(prev_db, latest_db)
    generate_db_delta(out_p, delta_obj, int(prev_db_ver), m)

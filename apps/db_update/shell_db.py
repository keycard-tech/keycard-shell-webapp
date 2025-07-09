
import json
import struct
import hashlib

from apps.db_update.abi import process_abi, serialize_abi
from apps.db_update.token_db import process_token, serialize_chain, serialize_token
from common.consts import PAGE_SIZE, VERSION_MAGIC, WORD_SIZE
from common.errors import InvalidAbiList, InvalidTokenList
from common.utils import sign

def pad_write(f, buf):
    f.write(buf)
    
    size = len(buf)
    padlen = WORD_SIZE - (size % WORD_SIZE)

    while padlen > 0:
        f.write((0x80 | padlen).to_bytes(1))
        padlen = padlen - 1
        size = size + 1

    while size < PAGE_SIZE:
        f.write(0xff.to_bytes(1))
        size = size + 1

def db_write(f, m, buf, entry):
    if m != None:
        m.update(entry)
        f.write(entry)
        return b''
    
    if len(buf) + len(entry) <= PAGE_SIZE:
        return buf + entry
    else:
        pad_write(f, buf)
        return entry

def serialize_db(f, m, chains, tokens, abis, db_version, db_h):
  db_buffer = db_write(f, m, b'', struct.pack("<HHI", VERSION_MAGIC, 4, db_version))
  
  for chain in chains.values():
    serialized_chain = serialize_chain(chain)
    db_buffer = db_write(f, m, db_buffer, serialized_chain)

  for token in tokens.values():
    serialized_token = serialize_token(token)
    db_buffer = db_write(f, m, db_buffer, serialized_token)

  for abi in abis.values():
    serialized_abi = serialize_abi(abi)
    db_buffer = db_write(f, m, db_buffer, serialized_abi)
        
  if len(db_buffer) > 0:
    pad_write(f, db_buffer)  

  db_h.update(db_buffer[8:]) 
  
def generate_token_bin_file(token_list, chain_list, abi_list, output, db_version):
  token_list = json.load(open(token_list))
  chain_list = json.load(open(chain_list))
  abi_list = json.load(open(abi_list))
    
  m = hashlib.sha256()
  db_h = hashlib.sha256()

  tokens = {}
  chains = {}
  abis = {}

  try:
    for token in token_list["tokens"]:
      process_token(tokens, chains, token, chain_list)
  except Exception as err:
      raise InvalidTokenList       
    
  try:
    for abi in abi_list:
      process_abi(abis, abi)
  except Exception as err:
      raise InvalidAbiList        

  with open(output, 'wb') as f:
    serialize_db(f, m, chains, tokens, abis, db_version, db_h)
    m_hash = m.digest()
    signature = sign(m_hash)
    db_hash = db_h.digest()
    f.write(signature)
  
  return db_hash.hex()

import os
import shutil
import zipfile

from secp256k1Crypto import PrivateKey

SIGN_KEY = os.environ['DB_SIGN_KEY']

def iter_query(query, field_name):
  res = []
  for e in query:
    res.append(getattr(e, field_name))
  return res

def zip_db_files(db_path, zip_path):
  with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
    for fp in db_path.glob("**/*"):
      if fp.suffix in {".json", ".bin"}:
        zipf.write(fp, arcname=fp.relative_to(db_path))

def makedirs(path):
  try:
    os.makedirs(path)
  except OSError as e:
    if e.errno == 17:
      pass

def deletedirs(path):
  if os.path.exists(path):
    shutil.rmtree(path)

def sign(m):
  key = PrivateKey(bytes(bytearray.fromhex(SIGN_KEY)), raw=True)
  sig = key.ecdsa_sign(m, raw=True)
  return key.ecdsa_serialize_compact(sig)
import hashlib
from common.consts import FW_VERSION_POS
from common.errors import InvalidFirmwareError
from common.utils import deletedirs
from django.conf import settings

def upload_file(file, output, write_type, enc, nl):
  with open(output, write_type, encoding=enc, newline=nl) as f:
    f.write(file)
    
def calc_fw_hash(data):
  fw_h = hashlib.sha256()
  fw_h.update(data)
  return fw_h.digest().hex()
      

def validate_firmware(fw, version):
  fw_ver = list(map(int, version.split("."))) 
  exp_fw_ver = []
  
  for i in range(FW_VERSION_POS, FW_VERSION_POS + 3, 1):
    exp_fw_ver.append(fw[i])

  if fw_ver != exp_fw_ver:
    raise InvalidFirmwareError(".".join(map(str, exp_fw_ver)), version)
  else:
    return True   

def delete_fw(fw_version):
  p = settings.MEDIA_ROOT + "/" + fw_version
  deletedirs(p)
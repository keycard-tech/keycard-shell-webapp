from common.utils import deletedirs
from django.conf import settings

def upload_file(file, output, write_type, enc, nl):
        with open(output, write_type, encoding=enc, newline=nl) as f:
           f.write(file)

def delete_fw(fw_version):
    p = settings.MEDIA_ROOT + "/" + fw_version
    deletedirs(p)
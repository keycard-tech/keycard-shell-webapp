class InvalidJSONFileError(Exception):
   def __init__(self, path):
        self.path = path   
class ProcessTokenError(Exception):
    def __init__(self, path):
        self.path = path   
class InvalidChainDBFile(Exception):
    def __init__(self, err):
        self.err = err   
class InvalidTokenDBFile(Exception):
   def __init__(self, err):
        self.err = err   
class InvalidAddressLength(Exception):
      pass
class InvalidTokenList(Exception):
    pass 
  
class InvalidAbiList(Exception):
  pass  
class ZipError(Exception):
    def __init__(self, path):
        self.path = path
class InvalidBinFileError(Exception):
    def __init__(self, path):
        self.path = path
class CompareDeltasError(Exception):
    def __init__(self, prev_db_version, latest_db_version):
        self.prev_db = prev_db_version
        self.latest_db = latest_db_version
class DecodeEntryError(Exception):
    pass
class SerializeDeltaError(Exception):
    def __init__(self, delta_db_version):
        self.delta_version = delta_db_version 
class InvalidFirmwareError(Exception):
    def __init__(self, exp_fw_ver, fw_ver):
        self.fw_ver = fw_ver  
        self.exp_fw_ver = exp_fw_ver    

def get_error_message(error):
    error_type = type(error).__name__
    if error_type == "InvalidFirmwareError":
        return f"Error: Firmware version doesn't match. Expected {error.exp_fw_ver}, got {error.fw_ver}"
    elif error_type == "FileNotFoundError":
        return f"Error: no such file or directory. {error}"
    elif error_type == "InvalidJSONFileError":
        return "Invalid JSON at " +  error.path
    elif error_type == "ProcessTokenError":
        return f"Error processing token. {error.err}"
    elif error_type == "InvalidChainDBFile":
        return f"Can't create db.bin. Error: {error.err}"
    elif error_type == "InvalidTokenDBFile":
        return f"Can't create db.bin. Error: {error.err}"
    elif error_type == "InvalidAddressLength":
        return "Unexpected address format"
    elif error_type == "InvalidTokenList":
        return "Processing token list. Error: Invalid JSON"
    elif error_type == "InvalidBinFileError":
        return f"Invalid bin file at {error.path}"
    elif error_type == "CompareDeltasError":
        return f"Error comparing {error.prev_db} and {error.latest_db}"
    elif error_type == "SerializeDeltaError":
        return f"Unable to create {error.delta_version} delta"
    elif error_type == "ZipError":
        return f"Unable to zip {error.path}"
    elif error_type == "Exception":
        return error

     
               

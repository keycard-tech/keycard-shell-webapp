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

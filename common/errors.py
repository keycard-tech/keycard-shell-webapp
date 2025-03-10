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
      def __init__(self, mess):
        self.message = mess   

class InvalidTokenList(Exception):
    def __init__(self, mess):
        self.message = mess   

class ZipError(Exception):
    def __init__(self, mess):
        self.message = mess

class InvalidBinFileError(Exception):
    def __init__(self, path):
        self.path = path

class CompareDeltasError(Exception):
    def __init__(self, prev_db_version, latest_db_version):
        self.prev_db = prev_db_version
        self.latest_db = latest_db_version

class SerializeDeltaError(Exception):
    def __init__(self, mess):
        self.message = mess

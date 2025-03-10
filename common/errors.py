class InvalidJSONFileError(Exception):
   def __init__(self, path):
        self.path = path   
        super().__init__(self.path)       
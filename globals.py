from Utils.path_utils import get_relative_path

# Global variables
fileName = 'test.csv'
outputDateFormat = '%Y-%m-%d'
logPath = get_relative_path('logs', __file__)

class LogFileName():
    _instance = None
    _logFileName = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(LogFileName, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self):
        pass

    def get_file(self):
        return self._logFileName
    
    def set_file(self, filename: str):
        self._logFileName = filename

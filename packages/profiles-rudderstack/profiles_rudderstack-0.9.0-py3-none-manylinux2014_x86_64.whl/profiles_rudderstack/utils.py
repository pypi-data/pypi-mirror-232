import logging
class RefManager:
    def __init__(self):
        self.refsDict = {}
        self.refId = 1

    def createRef(self, obj):
        refId = self.refId
        self.refsDict[refId] = obj
        self.refId += 1
        return refId
    
    def createRefWithKey(self, key: str, obj):
        self.refsDict[key] = obj
    
    def getRef(self, refId):
        return self.refsDict.get(refId, None)
    
def GetLogger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s    %(levelname)s    python/%(name)s    %(message)s', datefmt='%Y-%m-%d %H:%M:%S%z'))
    logger.addHandler(handler)
    return logger
import hashlib
from inspect import getsource
from typing import Tuple
from abc import ABC, abstractmethod
from profiles_rudderstack.material import WhtMaterial

class PyNativeRecipe(ABC):
    @abstractmethod
    def Prepare(self, this: WhtMaterial):
        raise NotImplementedError()

    @abstractmethod
    def Execute(self, this: WhtMaterial):
        raise NotImplementedError()
        
    @abstractmethod
    def Describe(self, this: WhtMaterial) -> Tuple[str, str]:
        raise NotImplementedError()
    
    def Hash(self):
        prepareCode = getsource(self.Prepare)
        executeCode = getsource(self.Execute)
        describeCode = getsource(self.Describe)

        hash = hashlib.sha256()
        hash.update(prepareCode.encode('utf-8'))
        hash.update(executeCode.encode('utf-8'))
        hash.update(describeCode.encode('utf-8'))

        return hash.hexdigest()
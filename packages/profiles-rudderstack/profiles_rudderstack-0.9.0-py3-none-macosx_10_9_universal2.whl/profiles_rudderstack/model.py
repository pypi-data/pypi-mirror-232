from typing import Tuple, Optional
from abc import ABC, abstractmethod
from profiles_rudderstack.recipe import PyNativeRecipe
from profiles_rudderstack.contract import Contract

class BaseModelType(ABC):
    TypeName = "base_model_type"
    # Json Schema
    BuildSpecSchema = {}

    def __init__(self, buildSpec: dict, schemaVersion: int, pbVersion: str) -> None:
        self.buildSpec = buildSpec
        self.schemaVersion = schemaVersion
        self.pbVersion = pbVersion

    def GetContract(self) -> Optional[Contract]:
        return None
    
    def GetEntityKey(self) -> Optional[str]:
        return None
    
    @abstractmethod
    def GetMaterialRecipe(self) -> PyNativeRecipe:
        raise NotImplementedError()
    
    @abstractmethod
    def Validate(self) -> Tuple[bool, str]:
        if self.schemaVersion < 43:
            return False, "schema version should >= 43"
        return True, ""

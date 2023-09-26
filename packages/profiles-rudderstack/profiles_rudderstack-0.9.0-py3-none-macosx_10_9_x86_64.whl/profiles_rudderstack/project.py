import inspect
from google.protobuf import struct_pb2, json_format
import json
from typing import Type, cast
from types import FrameType
from profiles_rudderstack.tunnel.tunnel_pb2_grpc import WhtServiceStub
from profiles_rudderstack.model import BaseModelType
from profiles_rudderstack.utils import RefManager, GetLogger
import profiles_rudderstack.tunnel.tunnel_pb2 as tunnel_pb2

class WhtProject:
    def __init__(self, project_ref: int, currentSupportedSchemaVersion: int, pbVersion: str, refManager: RefManager, whtService: WhtServiceStub):
        self.project_ref = project_ref
        self.__whtService = whtService
        self.__refManager = refManager
        self.currentSupportedSchemaVersion = currentSupportedSchemaVersion
        self.pbVersion = pbVersion
        self.logger = GetLogger("WhtProject")

    def __createFactoryFunc(self, modelClass: Type[BaseModelType], modelType: str):
        def factory(baseProjRef:int, modelName: str, buildSpec: dict):
            model = modelClass(buildSpec, self.currentSupportedSchemaVersion, self.pbVersion)
            entityKey = model.GetEntityKey()

            newPyModelResponse: tunnel_pb2.NewPythonModelResponse = self.__whtService.NewPythonModel(tunnel_pb2.NewPythonModelRequest(
                name=modelName,
                model_type=modelType,
                build_spec=json.dumps(buildSpec),
                base_proj_ref=baseProjRef,
                entity_key=entityKey,
            ))

            whtModelRef = newPyModelResponse.model_ref
            pyModelRef = self.__refManager.createRef(model)
            contract = model.GetContract()

            return whtModelRef, pyModelRef, contract.getContractRef() if contract else None
        
        return factory

    def RegisterModelType(self, modelClass: Type[BaseModelType]):
        package_name = ""
        # Get the package name from caller, from RegisterExtensions
        frame_type = cast(FrameType, cast(FrameType, inspect.currentframe()).f_back)
        package_info = inspect.getmodule(frame_type)
        if package_info:
            mod = package_info.__name__.split('.')
            package_name = mod[0]
            self.logger.info(f"Registering {modelClass.TypeName} from {package_name}")

        modelType = modelClass.TypeName
        schema = struct_pb2.Struct()
        json_format.ParseDict(modelClass.BuildSpecSchema, schema)

        self.__whtService.RegisterModelType(tunnel_pb2.RegisterModelTypeRequest(
            model_type=modelType, 
            build_spec_schema=schema,
            project_ref=self.project_ref,
        ))

        factory = self.__createFactoryFunc(modelClass, modelType)
        self.__refManager.createRefWithKey(modelType, {
            "factoryFunc": factory,
            "package": package_name,
        })
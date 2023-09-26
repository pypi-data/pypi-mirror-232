from typing import Optional
from profiles_rudderstack.contract import Contract
from profiles_rudderstack.tunnel.tunnel_pb2_grpc import WhtServiceStub
import profiles_rudderstack.tunnel.tunnel_pb2 as tunnel_pb2

class WhtWarehouseClient:
    def __init__(self, materialRef: int, whtService: WhtServiceStub) -> None:
        self.__whtService = whtService
        self.__materialRef = materialRef

    def QuerySqlWithoutResult(self, sql: str):
        self.__whtService.QuerySqlWithoutResult(tunnel_pb2.QuerySqlWithoutResultRequest(
            material_ref=self.__materialRef,
            sql=sql,
        ))
    
    def QueryTemplateWithoutResult(self, template: str):
        self.__whtService.QueryTemplateWithoutResult(tunnel_pb2.QueryTemplateWithoutResultRequest(
            material_ref=self.__materialRef,
            template=template,
        ))

class WhtContext:
    def __init__(self, materialRef: int, whtService: WhtServiceStub) -> None:
        self.__materialRef = materialRef
        self.__whtService = whtService
        self.client = WhtWarehouseClient(materialRef, whtService)

    def IsNullContext(self) -> bool:
        nullCtxResponse: tunnel_pb2.IsNullContextResponse = self.__whtService.IsNullContext(tunnel_pb2.IsNullContextRequest(
            material_ref=self.__materialRef,
        ))
        return nullCtxResponse.is_null_ctx

class WhtMaterial:
    def __init__(self, materialRef: int, whtService: WhtServiceStub):
        self.__materialRef = materialRef
        self.__whtService = whtService
        self.whtCtx = WhtContext(materialRef, whtService)
        
    def Name(self) -> str:
        nameResponse: tunnel_pb2.NameResponse = self.__whtService.Name(tunnel_pb2.NameRequest(
            material_ref=self.__materialRef,
        ))

        return nameResponse.material_name

    def DeRef(self, modelPath: str, contract: Optional[Contract] = None):
        deRefResponse: tunnel_pb2.DeRefResponse = self.__whtService.DeRef(tunnel_pb2.DeRefRequest(
            material_ref=self.__materialRef,
            model_path=modelPath,
            contract_ref= contract.getContractRef() if contract is not None else None,
        ))

        return WhtMaterial(deRefResponse.material_ref, self.__whtService)
    
    def DeRefOptional(self, modelPath: str, contract: Optional[Contract] = None):
        deRefOptionalResponse: tunnel_pb2.DeRefResponse = self.__whtService.DeRefOptional(tunnel_pb2.DeRefRequest(
            material_ref=self.__materialRef,
            model_path=modelPath,
            contract_ref= contract.getContractRef() if contract is not None else None,
        ))

        return WhtMaterial(deRefOptionalResponse.material_ref, self.__whtService)
    
    def DeRefPreferred(self, modelPath: str, contract: Optional[Contract] = None):
        deRefPreferredResponse: tunnel_pb2.DeRefResponse = self.__whtService.DeRefPreferred(tunnel_pb2.DeRefRequest(
            material_ref=self.__materialRef,
            model_path=modelPath,
            contract_ref= contract.getContractRef() if contract is not None else None,
        ))

        return WhtMaterial(deRefPreferredResponse.material_ref, self.__whtService)
    
    def GetColumns(self):
        getAllColsResponse: tunnel_pb2.GetColumnsResponse = self.__whtService.GetColumns(tunnel_pb2.GetColumnsRequest(
            material_ref=self.__materialRef,
        ))

        return [{"name": col.name, "type": col.type} for col in getAllColsResponse.columns]
    
    def ExecuteTextTemplate(self, template: str) -> str:
        templateResponse: tunnel_pb2.ExecuteTextTemplateResponse = self.__whtService.ExecuteTextTemplate(tunnel_pb2.ExecuteTextTemplateRequest(
            material_ref=self.__materialRef,
            template=template,
        ))

        return templateResponse.result
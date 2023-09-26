import profiles_rudderstack.tunnel.tunnel_pb2 as tunnel_pb2

class Contract:
    def __init__(self, contractRef: int) -> None:
        self.__contractRef = contractRef

    def getContractRef(self) -> int:
        return self.__contractRef

def BuildContract(contract: str) -> Contract:
    # This is a workaround as WhtService is not available globally while initialisation
    from profiles_rudderstack.wht_service import WhtService
    contractRes: tunnel_pb2.BuildContractResponse = WhtService.BuildContract(
        tunnel_pb2.BuildContractRequest(contract=contract)
    )
    return Contract(contractRes.contract_ref)
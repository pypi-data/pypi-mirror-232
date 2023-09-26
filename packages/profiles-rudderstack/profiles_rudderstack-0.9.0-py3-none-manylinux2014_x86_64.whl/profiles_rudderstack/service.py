import json, grpc, importlib.util, importlib.metadata, pkg_resources
from packaging.requirements import Requirement
from typing import Callable, List, Union

from profiles_rudderstack.model import BaseModelType
from profiles_rudderstack.recipe import PyNativeRecipe
from profiles_rudderstack.material import WhtMaterial
from profiles_rudderstack.utils import RefManager, GetLogger
from profiles_rudderstack.project import WhtProject
import profiles_rudderstack.tunnel.tunnel_pb2 as tunnel_pb2
from profiles_rudderstack.tunnel.tunnel_pb2_grpc import PythonServiceServicer, WhtServiceStub

class ProfilesRpcService(PythonServiceServicer):
    def __init__(self, refManager: RefManager, whtService: WhtServiceStub, currentSupportedSchemaVersion: int, pbVersion: str):
        self.logger = GetLogger("ProfilesRpcService")
        self.currentSupportedSchemaVersion = currentSupportedSchemaVersion
        self.pbVersion = pbVersion
        self.refManager = refManager
        self.whtService = whtService
        
    def __registerModelType(self, package: str, project: WhtProject):
        requirement = Requirement(package)
        module = importlib.import_module(requirement.name)
        if module is None:
            return f"{requirement.name} not found" 

        registerFunc: Callable[[WhtProject],None] = getattr(module, "RegisterExtensions")
        if registerFunc is None:
            return f"RegisterModelType not found in {requirement.name}"

        registerFunc(project)
        return None
    
    def RegisterPackages(self, request: tunnel_pb2.RegisterPackagesRequest, context):
        not_installed: List[str] = []
        for package in request.packages:
            try:
                pkg_resources.require(package)
            except (pkg_resources.DistributionNotFound, pkg_resources.VersionConflict):
                not_installed.append(package)
        
        if not_installed:
            error_message = "The following package(s) are not installed or their version is not correct: {}.".format(", ".join(not_installed))
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(error_message)
            return tunnel_pb2.RegisterPackagesResponse()

        project = WhtProject(request.project_ref, self.currentSupportedSchemaVersion, self.pbVersion, self.refManager, self.whtService)
        for package in request.packages:
            err = self.__registerModelType(package, project)
            if err is not None:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(err)
                return tunnel_pb2.RegisterPackagesResponse()
        
        return tunnel_pb2.RegisterPackagesResponse()
    
    def GetPackageVersion(self, request: tunnel_pb2.GetPackageVersionRequest, context):
        modelTypeRef = self.refManager.getRef(request.model_type)
        if modelTypeRef is None:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("model type not found")
            return tunnel_pb2.GetPackageVersionResponse()

        package = modelTypeRef["package"]
        version = importlib.metadata.version(package)
        return tunnel_pb2.GetPackageVersionResponse(version=version)
    
    def ModelFactory(self, request: tunnel_pb2.ModelFactoryRequest, context):
        modelTypeRef = self.refManager.getRef(request.model_type)
        if modelTypeRef is None:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("model type not found")
            return tunnel_pb2.ModelFactoryResponse()
        
        buildSpec = json.loads(request.build_spec)
        whtModelRef, pyModelRef, contractRef = modelTypeRef["factoryFunc"](request.base_proj_ref, request.model_name, buildSpec)
        
        return tunnel_pb2.ModelFactoryResponse(wht_model_ref=whtModelRef, python_model_ref=pyModelRef, contract_ref=contractRef)
    
    ### Model methods

    def GetMaterialRecipe(self, request: tunnel_pb2.GetMaterialRecipeRequest, context):
        model: Union[BaseModelType, None] = self.refManager.getRef(request.py_model_ref)
        if model is None:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("model not found")
            return tunnel_pb2.GetMaterialRecipeResponse()
        
        recipe = model.GetMaterialRecipe()
        recipeRef = self.refManager.createRef(recipe)
        return tunnel_pb2.GetMaterialRecipeResponse(recipe_ref=recipeRef)
    
    def DescribeRecipe(self, request: tunnel_pb2.DescribeRecipeRequest, context):
        recipe: Union[PyNativeRecipe, None] = self.refManager.getRef(request.recipe_ref)
        if recipe is None:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("recipe not found")
            return tunnel_pb2.DescribeRecipeResponse()
        
        this = WhtMaterial(request.material_ref, self.whtService)
        description, extension = recipe.Describe(this)
        return tunnel_pb2.DescribeRecipeResponse(description=description, extension=extension)
    
    def PrepareRecipe(self, request: tunnel_pb2.PrepareRecipeRequest, context):
        recipe: Union[PyNativeRecipe, None] = self.refManager.getRef(request.recipe_ref)
        if recipe is None:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("recipe not found")
            return tunnel_pb2.PrepareRecipeResponse()
        
        this = WhtMaterial(request.material_ref, self.whtService)
        recipe.Prepare(this)
        return tunnel_pb2.PrepareRecipeResponse()
    
    def ExecuteRecipe(self, request: tunnel_pb2.ExecuteRecipeRequest, context):
        recipe: Union[PyNativeRecipe, None] = self.refManager.getRef(request.recipe_ref)
        if recipe is None:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("recipe not found")
            return tunnel_pb2.ExecuteRecipeResponse()
        
        this = WhtMaterial(request.material_ref, self.whtService)
        recipe.Execute(this)
        return tunnel_pb2.ExecuteRecipeResponse()
    
    def GetRecipeHash(self, request: tunnel_pb2.GetRecipeHashRequest, context):
        recipe: Union[PyNativeRecipe, None] = self.refManager.getRef(request.recipe_ref)
        if recipe is None:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("recipe not found")
            return tunnel_pb2.GetRecipeHashResponse()
        
        hash = recipe.Hash()
        return tunnel_pb2.GetRecipeHashResponse(hash=hash)
    
    def Validate(self, request: tunnel_pb2.ValidateRequest, context):
        model: Union[BaseModelType, None] = self.refManager.getRef(request.py_model_ref)
        if model is None:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("model not found")
            return tunnel_pb2.ValidateResponse()

        isValid, reason = model.Validate()
        return tunnel_pb2.ValidateResponse(valid=isValid, reason=reason)

    ### Ping
    
    def Ping(self, request, context):
        return tunnel_pb2.PingResponse(message="ready")

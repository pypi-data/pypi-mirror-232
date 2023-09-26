from moorse.service.auth_service import AuthService
from moorse.clients.template_client import TemplateClient
from moorse.dto.template.request.template_request import TemplateRequest
from moorse.dto.template.template_dto import TemplateDto
from moorse.dto.template.response.multiple.template_list import TemplateList

class TemplateService:

    __auth: AuthService

    def __init__(self, auth: AuthService):
        self.__auth = auth

    def create(self, template: TemplateRequest) -> TemplateDto:
        return TemplateClient().create(self.__auth.get_token(), template)

    def get_all(self) -> TemplateList:
        return TemplateClient().get_all(self.__auth.get_token())

    def get_one(self, template_id: str) -> TemplateDto:
        return TemplateClient().get_one(self.__auth.get_token(), template_id)
    
    def delete(self, template_id: str) -> TemplateDto:
        return TemplateClient().delete(self.__auth.get_token(), template_id)
from moorse.dto.message.template.parameter.parameter import Parameter
from moorse.dto.message.template.parameter.file_info.document_info import DocumentInfo

class DocumentParameter(Parameter):

    def __init__(self, url: str, filename: str):
        super().__init__("document", None, None, DocumentInfo(url, filename), None)
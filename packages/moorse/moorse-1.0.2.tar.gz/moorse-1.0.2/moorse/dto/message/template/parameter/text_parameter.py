from moorse.dto.message.template.parameter.parameter import Parameter

class ImageParameter(Parameter):

    def __init__(self, text: str):
        super().__init__("text", text, None, None, None)
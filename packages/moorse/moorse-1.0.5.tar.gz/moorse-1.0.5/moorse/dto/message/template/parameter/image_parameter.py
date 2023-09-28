from moorse.dto.message.template.parameter.parameter import Parameter
from moorse.dto.message.template.parameter.file_info.image_info import ImageInfo

class ImageParameter:

    def __init__(self, url: str):
        super().__init__("image", None, ImageInfo(url), None, None)
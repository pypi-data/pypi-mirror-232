from moorse.dto.message.template.parameter.file_info.image_info import ImageInfo
from moorse.dto.message.template.parameter.file_info.document_info import DocumentInfo
from moorse.dto.message.template.parameter.file_info.video_info import VideoInfo

class Parameter:

    type: str
    text: str
    image: ImageInfo
    document: DocumentInfo
    video: VideoInfo

    def __init__(
        self, 
        type: str, 
        text: str, 
        image: ImageInfo, 
        document: DocumentInfo, 
        video: VideoInfo
    ):
        self.type = type
        self.text = text
        self.image = image
        self.document = document
        self.video = video

    def to_json(self):
        return {
            "type": self.type,
            "text": self.text if self.text else None,
            "image": self.image.to_json() if self.image else None,
            "document": self.document.to_json() if self.document else None,
            "video": self.video.to_json() if self.video else None
        }
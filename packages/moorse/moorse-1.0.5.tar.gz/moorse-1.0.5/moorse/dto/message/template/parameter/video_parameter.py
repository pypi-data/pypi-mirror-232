from moorse.dto.message.template.parameter.parameter import Parameter
from moorse.dto.message.template.parameter.file_info.video_info import VideoInfo

class VideoParameter(Parameter):

    def __init__(self, url: str):
        super().__init__("video", None, None, None, VideoInfo(url))
        self.url = url
class VideoInfo:

    link: str

    def __init__(self, link: str):
        self.link = link

    def to_json(self):
        return {
            "link": self.link
        }
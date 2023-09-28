class DocumentInfo:

    link: str
    filename: str

    def __init__(self, link: str, filename: str):
        self.link = link
        self.filename = filename

    def to_json(self):
        return {
            "link": self.link,
            "filename": self.filename
        }
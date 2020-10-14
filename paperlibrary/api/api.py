from typing import List

from requests import Session

from paperlibrary.api.models import Author, PDF


class PaperLibraryAPI:

    def __init__(self, baseURL: str, auth_token: str):
        self.baseURL = baseURL
        self.auth_token = auth_token
        self.s = Session()
        self.s.headers.update({"Authorization": "Token " + auth_token})

    def fetch_authors(self) -> List[Author]:
        r = self.s.get(self.baseURL + "authors/")
        return Author.schema().loads(r.text, many=True)

    def fetch_pdfs(self) -> List[PDF]:
        r = self.s.get(self.baseURL + "pdfs/")
        return PDF.schema().loads(r.text, many=True)

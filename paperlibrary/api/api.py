from pathlib import Path
from typing import List, Dict

from requests import Session

from paperlibrary.api.models import Author, PDF, Keyword, PaperComplete


class PaperLibraryAPI:

    def __init__(self, baseURL: str, auth_token: str):
        self.baseURL = baseURL
        self.auth_token = auth_token
        self.s = Session()
        self.s.headers.update({"Authorization": "Token " + auth_token})

    def fetch_papers(self) -> List[PaperComplete]:
        r = self.s.get(self.baseURL + "papers/")
        return PaperComplete.schema().loads(r.text, many=True)

    def fetch_authors(self) -> List[Author]:
        r = self.s.get(self.baseURL + "authors/")
        return Author.schema().loads(r.text, many=True)

    def fetch_keywords(self) -> List[Keyword]:
        r = self.s.get(self.baseURL + "keywords/")
        return Keyword.schema().loads(r.text, many=True)

    def fetch_papers_by_year(self) -> Dict[int, List[PaperComplete]]:
        papers = self.fetch_papers()
        years: Dict[int, List[PaperComplete]] = {}
        for paper in papers:
            if paper.year in years:
                years[paper.year].append(paper)
            else:
                years[paper.year] = [paper]
        return years

    def fetch_pdfs(self) -> List[PDF]:
        r = self.s.get(self.baseURL + "pdfs/")
        return PDF.schema().loads(r.text, many=True)

    def upload_pdf(self, pdf, file: Path) -> PDF:
        with file.open("rb") as f:
            r = self.s.put(pdf.url, files={
                "file": f,
            })
        return PDF.schema().loads(r.text)

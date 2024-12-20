from functools import lru_cache
from pathlib import Path
from typing import List, Dict

from requests import Session

from paperlibrary.api.models import Author, PDF, Keyword, PaperComplete, Note


class PaperLibraryAPI:

    def __init__(self, baseURL: str, auth_token: str):
        self.baseURL = baseURL
        self.auth_token = auth_token
        self.s = Session()
        self.s.headers.update({"Authorization": "Token " + auth_token})

    @lru_cache
    def fetch_papers(self) -> List[PaperComplete]:
        r = self.s.get(self.baseURL + "papers/")
        r.raise_for_status()
        return [PaperComplete(**item) for item in r.json()]

    @lru_cache
    def fetch_authors(self) -> List[Author]:
        r = self.s.get(self.baseURL + "authors/")
        r.raise_for_status()
        return [Author(**item) for item in r.json()]

    @lru_cache
    def fetch_keywords(self) -> List[Keyword]:
        r = self.s.get(self.baseURL + "keywords/")
        r.raise_for_status()
        return [Keyword(**item) for item in r.json()]

    @lru_cache
    def fetch_papers_by_year(self) -> Dict[int, List[PaperComplete]]:
        papers = self.fetch_papers()
        years: Dict[int, List[PaperComplete]] = {}
        for paper in papers:
            if paper.year in years:
                years[paper.year].append(paper)
            else:
                years[paper.year] = [paper]
        return years

    @lru_cache
    def fetch_bibliography(self, tag=None) -> str:
        r = self.s.get(self.baseURL + "bibtex/", params={"tag": tag})
        r.raise_for_status()
        return r.text

    @lru_cache
    def fetch_pdfs(self) -> List[PDF]:
        r = self.s.get(self.baseURL + "pdfs/")
        r.raise_for_status()
        return [PDF(**item) for item in r.json()]

    def upload_pdf(self, pdf, file: Path) -> PDF:
        with file.open("rb") as f:
            r = self.s.put(pdf.url, files={
                "file": f,
            })
            r.raise_for_status()

        return PDF.model_validate_json(r.text)

    def update_note(self, id: int, file_text: str) -> Note:
        r = self.s.put(self.baseURL + f"notes/{id}/", json={"paper": id, "text_md": file_text})
        r.raise_for_status()
        return Note.model_validate_json(r.text)


    def create_note(self, id: int, file_text: str) -> Note:
        r = self.s.post(self.baseURL + f"notes/", json={"paper": id, "text_md": file_text})
        r.raise_for_status()
        return Note.model_validate_json(r.text)

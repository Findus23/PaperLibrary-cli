from typing import Optional, List

from pydantic import BaseModel


class PDF(BaseModel):
    id: int
    url: str
    file: str
    sha256: str
    type: str
    preview: Optional[str]
    # updated_at: datetime = field(
    #     metadata=config(
    #         encoder=datetime.isoformat,
    #         decoder=datetime.fromisoformat,
    #         mm_field=fields.DateTime(format='iso')
    #     )
    # )


class Paper(BaseModel):
    id: int
    url: str
    title: str
    custom_title: str
    pdfs: List[PDF]
    doi: Optional[str]

    @property
    def main_pdf(self) -> Optional[PDF]:
        if not self.pdfs:
            return None
        return self.pdfs[0]


class PaperComplete(Paper):
    keywords: List[str]
    authors: List[str]
    first_author: str
    publication: str
    doctype: str
    arxiv_id: Optional[str]
    arxiv_class: Optional[str]
    ads_version: Optional[int]
    bibcode: Optional[str]
    year: int
    pubdate: str  # TODO: to datetime
    entry_date: str  # TODO: to datetime
    citation_count: Optional[int]
    citation_key: Optional[str]
    recommended_by: List[str]
    tags: List[str]
    citename: Optional[str]
    custom_title: str
    notes_md: Optional[str]
    notes_html: Optional[str]
    notes_updated_at: Optional[str]


class Author(BaseModel):
    id: int
    url: str
    papers: List[Paper]
    name: str
    pretty_name: Optional[str]
    affiliation: Optional[str]
    orcid_id: Optional[str]

    @property
    def display_name(self):
        return self.pretty_name if self.pretty_name else self.name


class Keyword(BaseModel):
    id: int
    url: str
    papers: List[Paper]
    name: str
    kw_schema: str


class Note(BaseModel):
    paper: int
    text_md: str
    text_html: str
    updated_at: str

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

from dataclasses_json import DataClassJsonMixin, config
from marshmallow import fields


@dataclass
class PDF(DataClassJsonMixin):
    id: int
    url: str
    file: str
    sha256: str
    type: str
    preview: Optional[str]
    updated_at: datetime = field(
        metadata=config(
            encoder=datetime.isoformat,
            decoder=datetime.fromisoformat,
            mm_field=fields.DateTime(format='iso')
        )
    )


@dataclass
class Paper(DataClassJsonMixin):
    # id: int
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


@dataclass
class PaperComplete(Paper):
    keywords: List[str]
    authors: List[str]
    first_author: str
    publication: str
    doctype: str
    arxiv_id: Optional[str]
    bibcode: Optional[str]
    year: int
    pubdate: str  # TODO: to datetime
    entry_date: str  # TODO: to datetime
    citation_count: Optional[int]
    citation_key: Optional[str]
    recommended_by: List[str]
    tags: List[str]
    custom_title: str
    notes_md: str
    notes_html: str


@dataclass
class Author(DataClassJsonMixin):
    url: str
    papers: List[Paper]
    name: str
    pretty_name: Optional[str]
    affiliation: Optional[str]
    orcid_id: Optional[str]

    @property
    def display_name(self):
        return self.pretty_name if self.pretty_name else self.name


@dataclass
class Keyword(DataClassJsonMixin):
    url: str
    papers: List[Paper]
    name: str
    kw_schema: str

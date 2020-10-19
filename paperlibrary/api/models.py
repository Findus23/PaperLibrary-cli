from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

from dataclasses_json import DataClassJsonMixin, config
from marshmallow import fields


@dataclass
class PDF(DataClassJsonMixin):
    id: int
    file: str
    sha265: str
    type: str
    preview: str
    updated_at: datetime = field(
        metadata=config(
            encoder=datetime.isoformat,
            decoder=datetime.fromisoformat,
            mm_field=fields.DateTime(format='iso')
        )
    )


@dataclass
class Paper(DataClassJsonMixin):
    id: int
    url: str
    title: str
    pdfs: List[PDF]
    doi: str

    @property
    def main_pdf(self) -> PDF:
        return self.pdfs[0]


@dataclass
class Author(DataClassJsonMixin):
    url: str
    papers: List[Paper]
    name: str
    affiliation: Optional[str]
    orcid_id: Optional[str]


@dataclass
class Keyword(DataClassJsonMixin):
    url: str
    papers: List[Paper]
    name: str
    schema: str

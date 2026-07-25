from pathlib import Path
from pydantic import BaseModel

from fastapi import Response

from lxml.etree import parse, tostring, _ElementTree, _Element

from typing import (
    Optional, List,
)


class XMLResponse(Response):
    media_type = "application/xml"

    def render(self, content: _Element | _ElementTree) -> bytes:
        return tostring(
            content,
            pretty_print=True,
            xml_declaration=True,
            encoding="UTF-8",
        )


class DocumentationSource(BaseModel):
    dir: Path

    @property
    def doclist(self) -> List[str]:
        return [
            path.stem
            for path in self.dir.iterdir()
            if path.is_file() and path.suffix == ".xml"
        ]

    def get_document(self, name: str) -> Optional[_ElementTree]:
        path = self.dir / f"{name}.xml"
        if path.is_file():
            with path.open("r") as f:
                return parse(f)
        return None
    
    def query_document(self, name: str, query: str) -> Optional[_Element]:
        doc = self.get_document(name)
        if doc is None:
            return None
        return doc.xpath(query)
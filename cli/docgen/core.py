from abc import ABC, abstractmethod
from pathlib import Path
from pydantic import BaseModel, Field

from lxml import etree
from lxml.etree import ElementTree, Element, _ElementTree, _Element, SubElement

from typing import (
    List, Set,
    ClassVar, Optional,
    Generic, TypeVar,
)


T = TypeVar("T")
class DocgenDirectory(BaseModel, Generic[T]):
    IGNORE_PATTERNS: ClassVar[Set[str]] = set()
    """
    File or directory names we should skip parsing for.
    """

    path: Path
    tree: List["DocgenDirectory | T"]

    @classmethod
    def parse_directory(cls, path: Path) -> "DocgenDirectory":
        tree: List["DocgenDirectory | T"] = []
        for child_path in path.iterdir():
            if child_path.name in cls.IGNORE_PATTERNS:
                continue
            elif child_path.is_dir():
                tree.append(cls.parse_directory(child_path))
            else:
                item = cls.parse_path(child_path)
                if item:
                    tree.append(item)
        return cls(
            path=path,
            tree=tree,
        )

    @classmethod
    @abstractmethod
    def parse_path(cls, path: Path) ->  Optional[T]:
        ...

    @property
    @abstractmethod
    def directory_element(self) -> _Element:
        ...

    @property
    def doctree(self) -> _ElementTree:
        return ElementTree(self.directory_element)

    @property
    def xml(self) -> str:
        return etree.tostring(
            self.doctree,
            pretty_print=True,
            xml_declaration=True,
            encoding="UTF-8",
        ).decode(encoding="utf-8")

import ast
from ast import (
    AST, Module,
    Import, ImportFrom,
    Assign, AnnAssign, Expr,
    FunctionDef, ClassDef,
    Name,
)
from pathlib import Path
from pydantic import BaseModel, Field

from lxml import etree
from lxml.etree import ElementTree, Element, _ElementTree, _Element, SubElement

from mistletoe import Document

from typing import (
    List, Tuple, Optional,
    ClassVar,
)


class MarkdownDocument(BaseModel):
    content: str
    name: Optional[str] = None

    @property
    def document(self) -> Document:
        return Document(self.content)

    @property
    def document_element(self) -> _Element:
        pass


class PythonDirectory(BaseModel):
    path: Path
    tree: List["PythonDirectory | PythonModule | MarkdownDocument"]

    @classmethod
    def parse_directory(cls, path: Path) -> "PythonDirectory":
        tree: List["PythonDirectory | PythonModule | MarkdownDocument"] = []
        for child_path in path.iterdir():
            if child_path.name in { "__pycache__", }:
                continue
            elif child_path.is_dir():
                tree.append(cls.parse_directory(child_path))
            elif child_path.suffix == ".py":
                tree.append(PythonModule.parse_file(child_path))
            elif child_path.suffix == ".md":
                tree.append(MarkdownDocument(
                    name=child_path.stem,
                    content=child_path.read_text()
                ))
        return cls(
            path=path,
            tree=tree,
        )

    @property
    def docstr(self) -> str:
        if self.init_mod:
            return self.init_mod.docstr
        return "TODO"

    @property
    def init_mod(self) -> Optional["PythonModule"]:
        for item in self.tree:
            if isinstance(item, PythonModule) and item.path.name == "__init__.py":
                return item
        return None

    @property
    def directory_element(self) -> _Element:
        root = Element("module")
        root.attrib["name"] = self.path.name

        if self.docstr:
            doc = SubElement(root, "doc")
            doc.text = self.docstr

        for item in self.tree:
            match item:
                case PythonDirectory():
                    root.append(item.directory_element)
                case PythonModule():
                    if item.path.name == "__init__.py":
                        root.insert(0, item.init_element)
                    else:
                        root.append(item.file_element)
                case str():
                    pass

        return root

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
        


class PythonModule(BaseModel):
    path: Path
    directory: Optional[PythonDirectory]
    module: Module

    model_config = {"arbitrary_types_allowed": True}

    @classmethod
    def parse_file(
        cls,
        path: Path,
        directory: Optional[PythonDirectory] = None
    ) -> "PythonModule":
        return cls(
            path=path,
            directory=directory,
            module=ast.parse(
                path.read_text(),
                filename=path.name,
            )
        )

    @property
    def docstr(self) -> str:
        return ast.get_docstring(self.module)

    @property
    def _imports(self) -> List[Import | ImportFrom]:
        return [
            stmt for stmt in self.module.body
            if isinstance(stmt, Import) or isinstance(stmt, ImportFrom)
        ]

    @property
    def imports(self) -> List["PythonImport"]:
        return [
            PythonImport(
                module=self,
                node=node
            ) for node in self._imports
        ]

    @property
    def topvars(self) -> List["PythonScopedVariable"]:
        return [
            PythonScopedVariable(
                node=stmt,
                scope=self,
            ) for stmt in self.module.body
            if isinstance(stmt, AnnAssign)
        ]

    @property
    def functions(self) -> List["PythonFunction"]:
        return [
            PythonFunction(
                module=self,
                node=node
            ) for node in self.module.body
            if isinstance(node, FunctionDef)
        ]

    @property
    def classes(self) -> List["PythonClass"]:
        return [
            PythonClass(
                module=self,
                node=node
            ) for node in self.module.body
            if isinstance(node, ClassDef)
        ]


    @property
    def file_element(self) -> _Element:
        root = Element("file")
        root.attrib["name"] = self.path.stem

        if self.docstr:
            doc = SubElement(root, "doc")
            doc.text = self.docstr

        if self._imports:
            ielm = Element("imports")
            for pimport in self.imports:
                ielm.append(pimport.import_element)
            root.append(ielm)

        for fvar in self.topvars:
            root.append(fvar.variable_element)

        for fnode in self.functions:
            root.append(fnode.function_element)

        for cnode in self.classes:
            root.append(cnode.class_element)
        
        return root

    @property
    def init_element(self) -> _Element:
        root = Element("init")
        return root


class PythonImport(BaseModel):
    module: PythonModule
    node: Import | ImportFrom

    model_config = {"arbitrary_types_allowed": True}

    @property
    def parent_names(self) -> List[str]:
        return self.name.split(".")[1:][::-1]

    @property
    def name(self) -> str:
        match self.node:
            case Import():
                return self.node.names[0].name
            case ImportFrom():
                return self.node.module
            case _:
                raise Exception

    @property
    def import_element(self) -> _Element:
        elem = Element("import")
        elem.attrib["module"] = self.name
        if isinstance(self.node, ImportFrom):
            for alias in self.node.names:
                item = Element("item")
                item.attrib["name"] = alias.name
                elem.append(item)
        return elem


class PythonFunction(BaseModel):
    module: PythonModule
    node: FunctionDef

    model_config = {"arbitrary_types_allowed": True}

    @property
    def function_element(self) -> _Element:
        elem = Element("func")
        elem.attrib["name"] = self.node.name
        return elem


class PythonClass(BaseModel):
    module: PythonModule
    node: ClassDef

    model_config = {"arbitrary_types_allowed": True}

    @property
    def class_element(self) -> _Element:
        elem = Element("class")
        elem.attrib["name"] = self.node.name
        return elem


class PythonScopedVariable(BaseModel):
    node: Assign | AnnAssign
    uses: List[Expr] = Field(default_factory=list)
    scope: Optional[PythonClass | PythonFunction | PythonModule] = None

    model_config = {"arbitrary_types_allowed": True}

    @property
    def variable_element(self) -> _Element:
        elem = Element("var")
        target = self.node.target
        match target:
            case Name():
                elem.attrib["name"] = target.id
            case _:
                raise Exception()
        if isinstance(self.node, AnnAssign):
            elem.attrib["type"] = self.node.annotation.id
        return elem


if __name__ == "__main__":
    root = PythonDirectory.parse_directory(Path("../server"))

    with Path("sample.xml").open("w") as f:
        f.write(root.xml)
    
    #main = root.
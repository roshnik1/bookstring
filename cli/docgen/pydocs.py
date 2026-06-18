import ast
from ast import (
    AST, Module,
    Import, ImportFrom,
    Assign, AnnAssign, Expr,
    FunctionDef, AsyncFunctionDef, ClassDef,
    Constant, Name, Subscript,
    stmt, expr,
    unparse, walk,
)
from pathlib import Path
from pydantic import BaseModel, Field

from lxml.etree import ElementTree, Element, _ElementTree, _Element, SubElement
from lxml import etree

from mistletoe import Document

from md_xml import XMLRenderer

from typing import (
    List, Tuple, Optional,
    ClassVar, Literal,
)


class MarkdownDocument(BaseModel):
    content: str
    name: Optional[str] = None

    @property
    def document(self) -> Document:
        return Document(self.content)

    @property
    def document_element(self) -> _Element:
        return XMLRenderer().render(self.document)


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
                tree.append(PythonModule.parse_pyfile(child_path))
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
    def docstr(self) -> MarkdownDocument:
        if self.init_mod and self.init_mod.docstr:
            return self.init_mod.docstr
        return MarkdownDocument(content="TODO")

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
            doc = self.docstr.document_element
            root.append(doc)

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
    def parse_pyfile(
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
    def docstr(self) -> Optional[MarkdownDocument]:
        dstr = ast.get_docstring(self.module)
        if dstr:
            return MarkdownDocument(
                content=dstr,
            )
        return None

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
            ).scan_statements(self.module.body) for stmt in self.module.body
            if isinstance(stmt, AnnAssign)
        ]

    @property
    def functions(self) -> List["PythonFunction"]:
        return [
            PythonFunction(
                scope=self,
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
            doc = self.docstr.document_element
            root.append(doc)

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
                assert self.node.module
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


class PythonTypeAnnotation(BaseModel):
    node: expr

    model_config = {"arbitrary_types_allowed": True}

    def _resolve_subscript_stack(self, elem: _Element, subsc: Subscript) -> _Element:
        value = subsc.value
        if isinstance(value, Name):
            name = value.id
        else:
            raise NotImplementedError(f"Need support for type '{type(value).__name__}'")
        
        sub: Optional[_Element] = None
        match name:
            case "List":
                elem.attrib["iter"] = "list"
            case "Type":
                elem.attrib["istype"] = "1"
            case _:
                sub = SubElement(elem, "type")
        
        if isinstance(subsc.slice, Subscript):
            return self._resolve_subscript_stack(sub or elem, subsc.slice)
        elif isinstance(subsc.slice, Name):
            elem.text = subsc.slice.id
        else:
            raise NotImplementedError(f"Need support for type '{type(value).__name__}'")

        return elem

    @property
    def type_element(self) -> _Element:
        elem = Element("type")
        match self.node:
            case Name():
                elem.text = self.node.id
            case Subscript():
                elem = self._resolve_subscript_stack(elem, self.node)
        return elem


class PythonFunction(BaseModel):
    scope: "PythonModule | PythonClass | PythonFunction"
    node: FunctionDef | AsyncFunctionDef

    model_config = {"arbitrary_types_allowed": True}

    @property
    def docstr(self) -> Optional[MarkdownDocument]:
        dstr = ast.get_docstring(self.node)
        if dstr:
            return MarkdownDocument(
                content=dstr,
            )
        return None

    @property
    def arguments(self) -> List[
        Tuple[
            str, Optional[PythonTypeAnnotation], Literal["pos", "any", "kw"]
        ]]:
        args = []

        args += [
            (
                arg.arg,
                PythonTypeAnnotation(node=arg.annotation) if arg.annotation else None,
                "pos"
            )
            for arg in self.node.args.posonlyargs
        ]

        args += [
            (
                arg.arg,
                PythonTypeAnnotation(node=arg.annotation) if arg.annotation else None,
                "any"
            )
            for arg in self.node.args.args
        ]

        args += [
            (
                arg.arg,
                PythonTypeAnnotation(node=arg.annotation) if arg.annotation else None,
                "any"
            )
            for arg in self.node.args.kwonlyargs
        ]

        return args

    @property
    def returns(self) -> Optional[PythonTypeAnnotation]:
        if self.node.returns:
            return PythonTypeAnnotation(node=self.node.returns)
        return None

    @property
    def _signature_element(self) -> _Element:
        elem = Element("sig")

        if self.returns:
            SubElement(elem, "returns").append(self.returns.type_element)
        else:
            elem.attrib["isvoid"] = "1"
        
        if self.arguments:
            args = SubElement(elem, "arguments")
            for name, ann, kind in self.arguments:
                arg = SubElement(args, "arg")
                if kind == "pos":
                    arg.attrib["isposonly"] = "1"
                if kind == "kw":
                    arg.attrib["iskwonly"] = "1"
                arg.attrib["name"] = name
                if ann:
                    arg.append(ann.type_element)
        else:
            elem.attrib["isstart"] = "1"
        
        return elem

    @property
    def function_element(self) -> _Element:
        if isinstance(self.scope, PythonModule):
            elem = Element("function")
        elif isinstance(self.scope, PythonClass):
            elem = Element("method")
        else:
            elem = Element("function")

        elem.attrib["name"] = self.node.name

        elem.append(self._signature_element)

        if self.docstr:
            elem.append(self.docstr.document_element)

        return elem


class PythonClass(BaseModel):
    module: PythonModule
    node: ClassDef
    outerclass: Optional["PythonClass"] = None

    model_config = {"arbitrary_types_allowed": True}

    @property
    def docstr(self) -> Optional[MarkdownDocument]:
        dstr = ast.get_docstring(self.node)
        if dstr:
            return MarkdownDocument(
                content=dstr,
            )
        return None

    @property
    def members(self) -> List["PythonScopedVariable"]:
        return [
            PythonScopedVariable(
                node=stmt,
                scope=self,
            ).scan_statements(self.node.body) for stmt in self.node.body
            if isinstance(stmt, AnnAssign)
        ]

    @property
    def methods(self) -> List["PythonFunction"]:
        return [
            PythonFunction(
                node=node,
                scope=self,
            ) for node in self.node.body
            if isinstance(node, FunctionDef)
        ]

    @property
    def innerclasses(self) -> List["PythonClass"]:
        return [
            PythonClass(
                module=self.module,
                node=node,
                outerclass=self,
            ) for node in self.node.body
            if isinstance(node, ClassDef)
        ]

    @property
    def class_element(self) -> _Element:
        elem = Element("class")

        elem.attrib["name"] = self.node.name

        for base in self.node.bases:
            inherit = SubElement(elem, "inherits")
            if isinstance(base, Name):
                scls = SubElement(inherit, "super")
                scls.attrib["name"] = base.id

        if self.docstr:
            elem.append(self.docstr.document_element)
        
        for fvar in self.members:
            elem.append(fvar.variable_element)

        for fnode in self.methods:
            elem.append(fnode.function_element)

        for cnode in self.innerclasses:
            elem.append(cnode.class_element)
        
        return elem


class PythonScopedVariable(BaseModel):
    node: AnnAssign
    docnode: Optional[str] = None
    uses: List[stmt] = Field(default_factory=list)
    scope: Optional[PythonClass | PythonFunction | PythonModule] = None

    model_config = {"arbitrary_types_allowed": True}

    @property
    def name(self) -> str:
        target = self.node.target
        match target:
            case Name():
                return target.id
            case _:
                raise Exception()

    @property
    def docstr(self) -> Optional[MarkdownDocument]:
        if self.docnode:
            return MarkdownDocument(
                content=self.docnode,
            )
        return None

    def scan_statements(self, body: List[stmt]) -> "PythonScopedVariable":
        defined: Optional[int] = None
        for i, statement in enumerate(body):
            if (
                defined and i == defined + 1
                and isinstance(statement, Expr) and isinstance(statement.value, Constant)
                and isinstance(statement.value.value, str)
            ):
                self.docnode = statement.value.value

            for node in walk(statement):
                if isinstance(node, Name) and node.id == self.name:
                    if not self.uses:
                        defined = i
                    self.uses.append(statement)
                    break
        return self

    @property
    def variable_element(self) -> _Element:
        elem = Element("var")
        elem.attrib["name"] = self.name

        if isinstance(self.node, AnnAssign):
            elem.attrib["type"] = self.node.annotation.id #type: ignore
        
        if self.docstr:
            elem.append(self.docstr.document_element)
        
        if self.uses:
            pass

        return elem


if __name__ == "__main__":
    root = PythonDirectory.parse_directory(Path("../server"))

    with Path("sample.xml").open("w") as f:
        f.write(root.xml)
    
    main = root.tree[0]
    svar = main.topvars[0]

    core = root.tree[1].tree[0]
    xmdl = core.classes[0]
    nmdl = core.classes[1]


    mutils = root.tree[2]
    fgetm = mutils.functions[0]
    fwrtm = mutils.functions[1]
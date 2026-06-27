from pathlib import Path
from pydantic import BaseModel

from config import DocsConf
from docgen.md_xml import MarkdownDocument, MarkdownDirectory
from docgen.pydocs import PythonDirectory
from docgen.tsdocs import TypeScriptDirectory

from typing import List


class DocumentationBuilder(BaseModel):
    root: Path
    conf: DocsConf

    @property
    def docs_dir(self) -> Path:
        return self.root / self.conf.output_dir

    @property
    def root_docs(self) -> MarkdownDirectory:
        docs = []
        for child_path in self.root.iterdir():
            if child_path.is_file() and child_path.suffix == ".md":
                docs.append(MarkdownDocument(
                    name=child_path.stem,
                    content=child_path.read_text(),
                ))
        return MarkdownDirectory(
            path=self.root,
            tree=docs,
        )

    def build(self):
        with (self.docs_dir / self.conf.root_name).with_suffix(".xml").open("w") as f:
            f.write(self.root_docs.xml)

        for known_dir in self.conf.known:
            match known_dir.lang:
                case "ts":
                    continue
                    parsed = TypeScriptDirectory.parse_directory(self.root / known_dir.dir)
                case "py":
                    parsed = PythonDirectory.parse_directory(self.root / known_dir.dir)
                case None:
                    parsed = MarkdownDirectory.parse_directory(self.root / known_dir.dir)

            with (self.docs_dir / known_dir.dir.name).with_suffix(".xml").open("w") as f:
                f.write(parsed.xml)
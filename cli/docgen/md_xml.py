"""
XML renderer for mistletoe.
"""

import yaml
from re import compile, Pattern, Match, MULTILINE
from pathlib import Path
from pydantic import BaseModel

from lxml.etree import Element, _Element, SubElement, CDATA

from itertools import chain
from urllib.parse import quote
from mistletoe import Document, block_token
from mistletoe import token, span_token
from mistletoe.block_token import HtmlBlock
from mistletoe.span_token import HtmlSpan
from mistletoe.base_renderer import BaseRenderer

from docgen.core import DocgenDirectory

from typing import List, Optional, ClassVar, Dict


class DirectiveToken(span_token.SpanToken):
    pattern: ClassVar[Pattern] = compile(
        r"@(?P<drt>[a-z]+)( (?P<name>[a-z\d_]+))? *(- (?P<msg>.+))?"
    )
    """
    Pattern to match at-directives, ex:

    ```
    @task fix_451 - Fix a thing
    ```

    This pattern generates three named groups on a match:
      + **drt**: Directive (required), lowercase ascii letters
      + **name**: Use name (optional), lowercase ascii, digits, and underscores
      + **msg**: Message content (optional), arbitrary string
    """

    directive: str
    """ Directive name (lowercase letters only)"""

    target: Optional[str] = None
    """ Target name (lowercase letters, digits, and underscores)"""

    message: Optional[str] = None
    """ Directive message """

    def __init__(self, regex: Match):
        self.directive = regex.group("drt")
        self.target = regex.group("name")
        self.message = regex.group("msg")


class GlossLink(span_token.SpanToken):
    pattern: ClassVar[Pattern] = compile(r"\[\[(?P<target>[\w\d \.\-_]+)\]\]")
    target: str

    def __init__(self, match_obj):
        self.target = match_obj.group("target")


class XMLRenderer(BaseRenderer):
    """
    XML renderer class.

    See mistletoe.base_renderer module for more info.
    See mistletoe.html_renderer module for template / baseline.
    """

    def __init__(self):
        self._suppress_ptag_stack = [False]
        super().__init__(
            DirectiveToken,
            GlossLink,
        )

    def __exit__(self, *args):
        super().__exit__(*args)

    def render(self, token: token.Token) -> _Element:
        return super().render(token)
    
    def render_directive_token(self, token: DirectiveToken) -> _Element:
        match token.directive:
            case "todo":
                elem = Element("task")
                elem.attrib["status"] = "unsorted"
            case "task":
                elem = Element("task")
                elem.attrib["status"] = "sorted"
            case _:
                elem = Element("directive")
                elem.attrib["key"] = token.directive
            
        if token.target:
            elem.attrib["name"] = token.target
        
        if token.message:
            elem.text = token.message
        return elem

    def render_children(self, element: _Element, children: List[token.Token]) -> _Element:
        if len(children) == 1 and isinstance(children[0], span_token.RawText):
            element.text = children[0].content
        else:
            for child in children:
                element.append(self.render(child))
        return element

    def render_to_plain(self, token: token.Token) -> _Element:
        elem = Element(token.__class__.__name__.lower())
        for child in token.children:
            elem.append(self.render_to_plain(child))
        if hasattr(token, "content"):
            elem.text = token.content #TODO handle escaping
        return elem

    def render_strong(self, token: span_token.Strong) -> _Element:
        elem = Element("strong")
        return self.render_children(elem, token.children)

    def render_emphasis(self, token: span_token.Emphasis) -> _Element:
        elem = Element("em")
        return self.render_children(elem, token.children)

    def render_inline_code(self, token: span_token.InlineCode) -> _Element:
        elem = Element("code")
        elem.text = CDATA(token.children[0].content) #type: ignore
        return self.render_children(elem, token.children)

    def render_strikethrough(self, token: span_token.Strikethrough) -> _Element:
        elem = Element("del")
        return self.render_children(elem, token.children)

    def render_image(self, token: span_token.Image) -> _Element:
        elem = Element("img")
        elem.attrib["url"] = self.escape_url(token.src)
        if token.title:
            elem.attrib["title"] = token.title
        if token.content:
            elem.attrib["alt"] = token.content
        if token.label:
            elem.attrib["label"] = token.label
        return elem

    def render_link(self, token: span_token.Link) -> _Element:
        elem = Element("link")

        elem.attrib["target"] = token.target

        if token.title:
            elem.attrib["title"] = token.title
        if token.label:
            elem.attrib["label"] = token.label

        if len(token.children) == 1 and ":" in token.children[0].content and len(token.children[0].content.split(":")) == 2:
            elem.attrib["tag"], elem.text = token.children[0].content.split(":")
            return elem

        return self.render_children(elem, token.children)
    
    def render_gloss_link(self, token: GlossLink) -> _Element:
        elem = Element("link")
        elem.attrib["kind"] = "gloss"
        elem.attrib["target"] = token.target
        elem.text = token.target
        return elem

    def render_auto_link(self, token: span_token.AutoLink) -> _Element:
        elem = Element("link")
        elem.attrib["target"] = self.escape_url(token.target)
        return self.render_children(elem, token.children)

    def render_escape_sequence(self, token: span_token.EscapeSequence) -> _Element:
        return self.render(token.children[0])

    def render_raw_text(self, token: span_token.RawText) -> _Element:
        elem = Element("span")
        elem.text = token.content
        return elem

    def render_heading(self, token: block_token.Heading) -> _Element:
        elem = Element("heading")
        elem.attrib["level"] = str(token.level)
        return self.render_children(elem, token.children)

    @staticmethod
    def render_html_span(token: span_token.HtmlSpan) -> str:
        raise NotImplementedError

    def render_quote(self, token: block_token.Quote) -> str:
        elements = ['<blockquote>']
        self._suppress_ptag_stack.append(False)
        elements.extend([self.render(child) for child in token.children])
        self._suppress_ptag_stack.pop()
        elements.append('</blockquote>')
        return '\n'.join(elements)

    def render_paragraph(self, token: block_token.Paragraph) -> _Element:
        elem = Element("p")
        return self.render_children(elem, token.children)

    def render_block_code(self, token: block_token.BlockCode) -> _Element:
        elem = Element("code")
        elem.text = CDATA(token.content)

        if token.language:
            elem.attrib["lang"] = token.language
        return elem

    def render_list(self, token: block_token.List) -> _Element:
        elem = Element("list")

        self._suppress_ptag_stack.append(not token.loose)
        for child in token.children:
            elem.append(self.render(child))
        self._suppress_ptag_stack.pop()

        return elem

    def render_list_item(self, token: block_token.ListItem) -> _Element:
        elem = Element("item")
        for child in token.children:
            chelm = self.render(child)
            if chelm.tag == "p":
                if chelm.text:
                    if elem.text:
                        elem.text += chelm.text
                    else:
                        elem.text = chelm.text
                if list(chelm):
                    elem.extend(list(chelm))
            else:
                elem.append(chelm)
        return elem

    def render_table(self, token: block_token.Table) -> str:
        raise NotImplemented
        # This is actually gross and I wonder if there's a better way to do it.
        #
        # The primary difficulty seems to be passing down alignment options to
        # reach individual cells.
        template = '<table>\n{inner}</table>'
        if hasattr(token, 'header'):
            head_template = '<thead>\n{inner}</thead>\n'
            head_inner = self.render_table_row(token.header, is_header=True)
            head_rendered = head_template.format(inner=head_inner)
        else:
            head_rendered = ''
        body_template = '<tbody>\n{inner}</tbody>\n'
        body_inner = self.render_inner(token)
        body_rendered = body_template.format(inner=body_inner)
        return template.format(inner=head_rendered + body_rendered)

    def render_table_row(self, token: block_token.TableRow, is_header=False) -> str:
        raise NotImplemented
        template = '<tr>\n{inner}</tr>\n'
        inner = ''.join([self.render_table_cell(child, is_header)
                         for child in token.children])
        return template.format(inner=inner)

    def render_table_cell(self, token: block_token.TableCell, in_header=False) -> str:
        raise NotImplemented
        template = '<{tag}{attr}>{inner}</{tag}>\n'
        tag = 'th' if in_header else 'td'
        if token.align is None:
            align = 'left'
        elif token.align == 0:
            align = 'center'
        elif token.align == 1:
            align = 'right'
        attr = ' align="{}"'.format(align)
        inner = self.render_inner(token)
        return template.format(tag=tag, attr=attr, inner=inner)

    @staticmethod
    def render_thematic_break(token: block_token.ThematicBreak) -> _Element:
        return Element("hr")

    @staticmethod
    def render_line_break(token: span_token.LineBreak) -> str:
        return Element("br")

    @staticmethod
    def render_html_block(token: block_token.HtmlBlock) -> str:
        raise NotImplemented
        return token.content

    def render_document(self, token: block_token.Document) -> _Element:
        self.footnotes.update(token.footnotes)
        doc = Element("doc")
        return self.render_children(doc, token.children)

    def escape_html_text(self, s: str) -> str:
        """
        Like `html.escape()`, but this  looks into the current rendering options
        to decide which of the quotes (double, single, or both) to escape.

        Intended for escaping text content. To escape content of an attribute,
        simply call `html.escape()`.
        """
        raise NotImplementedError
        s = s.replace("&", "&amp;")  # Must be done first!
        s = s.replace("<", "&lt;")
        s = s.replace(">", "&gt;")
        if self.html_escape_double_quotes:
            s = s.replace('"', "&quot;")
        if self.html_escape_single_quotes:
            s = s.replace('\'', "&#x27;")
        return s

    @staticmethod
    def escape_url(raw: str) -> str:
        """
        Escape urls to prevent code injection craziness. (Hopefully.)
        """
        #return html.escape(quote(raw, safe=URI_SAFE_CHARACTERS))
        return raw


class MarkdownDocument(BaseModel):
    content: str
    name: Optional[str] = None

    @property
    def data(self) -> Optional[Dict]:
        if self.content.startswith("---\n"):
            # YAML Frontmatter
            _, datablock, *_ = self.content.split("---")
            return yaml.safe_load(datablock)

    @property
    def nondata(self) -> str:
        if self.content.startswith("---\n"):
            _, _, *rest = self.content.split("---")
            return "---".join(rest)
        return self.content

    @property
    def document(self) -> Document:
        return Document(self.nondata)

    @property
    def document_element(self) -> _Element:
        doc = XMLRenderer().render(self.document)
        if self.name:
            doc.attrib["name"] = self.name
        if self.data:
            datablock = SubElement(doc, "data")
            for key, val in self.data.items():
                item = SubElement(datablock, "item")
                item.attrib["key"] = key
                item.attrib["value"] = val
        return doc


class MarkdownDirectory(DocgenDirectory[MarkdownDocument]):
    tree: List["MarkdownDocument | MarkdownDirectory"]

    @classmethod
    def parse_path(cls, path: Path) -> Optional[MarkdownDocument]:
        match path.suffix:
            case ".md":
                return MarkdownDocument(
                name=path.stem,
                content=path.read_text()
            )
            case _:
                pass

    @property
    def directory_element(self) -> _Element:
        root = Element("docsite")
        root.attrib["name"] = self.path.name

        for item in self.tree:
            match item:
                case MarkdownDirectory():
                    root.append(item.directory_element)
                case MarkdownDocument():
                    if item.name == "here":
                        root.insert(0, item.document_element)
                    else:
                        root.append(item.document_element)

        return root

"""
XML renderer for mistletoe.
"""

from lxml.etree import Element, _Element, SubElement, CDATA

from itertools import chain
from urllib.parse import quote
from mistletoe import block_token
from mistletoe import token, span_token
from mistletoe.block_token import HtmlBlock
from mistletoe.span_token import HtmlSpan
from mistletoe.base_renderer import BaseRenderer

from typing import List


class XMLRenderer(BaseRenderer):
    """
    XML renderer class.

    See mistletoe.base_renderer module for more info.
    See mistletoe.html_renderer module for template / baseline.
    """
    def __init__(
        self,
        *extras,
        **kwargs
    ):
        self._suppress_ptag_stack = [False]
        super().__init__(*extras, **kwargs)

    def __exit__(self, *args):
        super().__exit__(*args)

    def render(self, token: token.Token) -> _Element:
        return super().render(token)

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
        elem.attrib["target"] = self.escape_url(token.target)
        if token.title:
            elem.attrib["title"] = token.title
        if token.label:
            elem.attrib["label"] = token.label
        return self.render_children(elem, token.children)

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
        if self._suppress_ptag_stack[-1]:
            #return '{}'.format(self.render_inner(token))
            raise NotImplementedError
        elem = Element("p")
        return self.render_children(elem, token.children)

    def render_block_code(self, token: block_token.BlockCode) -> str:
        template = '<pre><code{attr}>{inner}</code></pre>'
        if token.language:
            attr = ' class="{}"'.format('language-{}'.format(html.escape(token.language)))
        else:
            attr = ''
        inner = self.escape_html_text(token.content)
        return template.format(attr=attr, inner=inner)

    def render_list(self, token: block_token.List) -> str:
        template = '<{tag}{attr}>\n{inner}\n</{tag}>'
        if token.start is not None:
            tag = 'ol'
            attr = ' start="{}"'.format(token.start) if token.start != 1 else ''
        else:
            tag = 'ul'
            attr = ''
        self._suppress_ptag_stack.append(not token.loose)
        inner = '\n'.join([self.render(child) for child in token.children])
        self._suppress_ptag_stack.pop()
        return template.format(tag=tag, attr=attr, inner=inner)

    def render_list_item(self, token: block_token.ListItem) -> str:
        if len(token.children) == 0:
            return '<li></li>'
        inner = '\n'.join([self.render(child) for child in token.children])
        inner_template = '\n{}\n'
        if self._suppress_ptag_stack[-1]:
            if token.children[0].__class__.__name__ == 'Paragraph':
                inner_template = inner_template[1:]
            if token.children[-1].__class__.__name__ == 'Paragraph':
                inner_template = inner_template[:-1]
        return '<li>{}</li>'.format(inner_template.format(inner))

    def render_table(self, token: block_token.Table) -> str:
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
        template = '<tr>\n{inner}</tr>\n'
        inner = ''.join([self.render_table_cell(child, is_header)
                         for child in token.children])
        return template.format(inner=inner)

    def render_table_cell(self, token: block_token.TableCell, in_header=False) -> str:
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
    def render_thematic_break(token: block_token.ThematicBreak) -> str:
        return '<hr />'

    @staticmethod
    def render_line_break(token: span_token.LineBreak) -> str:
        return '\n' if token.soft else '<br />\n'

    @staticmethod
    def render_html_block(token: block_token.HtmlBlock) -> str:
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
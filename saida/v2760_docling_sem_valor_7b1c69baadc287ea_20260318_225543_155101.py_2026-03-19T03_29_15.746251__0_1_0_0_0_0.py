class PatentHandler(ContentHandler):
    """SAX ContentHandler for patent documents."""
    APP_DOC_ELEMENT: Final[str] = 'us-patent-application'
    GRANT_DOC_ELEMENT: Final[str] = 'us-patent-grant'

    @unique
    class Element(Enum):
        """Represents an element of interest in the patent application document."""
        ABSTRACT = ('abstract', True)
        TITLE = ('invention-title', True)
        CLAIMS = ('claims', False)
        CLAIM = ('claim', False)
        CLAIM_TEXT = ('claim-text', True)
        PARAGRAPH = ('p', True)
        HEADING = ('heading', True)
        DESCRIPTION = ('description', False)
        TABLE = ('table', False)
        DRAWINGS = ('description-of-drawings', True)
        STYLE_SUPERSCRIPT = ('sup', True)
        STYLE_SUBSCRIPT = ('sub', True)
        MATHS = ('maths', False)

        @override
        def __new__(cls, value: str, _) -> Self:
            obj = object.__new__(cls)
            obj._value_ = value
            return obj

        @override
        def __init__(self, _, is_text: bool) -> None:
            self.is_text: bool = is_text

    @override
    def __init__(self) -> None:
        """Build an instance of the patent handler."""
        self.doc: DoclingDocument | None = None
        self.level: LevelNumber = 1
        self.parents: dict[LevelNumber, DocItem | None] = {1: None}
        self.property: list[str]
        self.claim: str
        self.claims: list[str]
        self.abstract: str
        self.text: str
        self._clean_data()
        self.style_html = HtmlEntity()

    @override
    def startElement(self, tag, attributes):
        """Signal the start of an element.

            Args:
                tag: The element tag.
                attributes: The element attributes.
            """
        if tag in (self.APP_DOC_ELEMENT, self.GRANT_DOC_ELEMENT):
            self.doc = DoclingDocument(name='file')
            self.text = ''
        self._start_registered_elements(tag, attributes)

    @override
    def skippedEntity(self, name):
        """Receive notification of a skipped entity.

            HTML entities will be skipped by the parser. This method will unescape them
            and add them to the text.

            Args:
                name: Entity name.
            """
        if self.property:
            elm_val = self.property[-1]
            element = self.Element(elm_val)
            if element.is_text:
                escaped = self.style_html.get_greek_from_iso8879(f'&{name};')
                unescaped = html.unescape(escaped)
                if unescaped == escaped:
                    _log.debug(f'Unrecognized HTML entity: {name}')
                    return
                if element in (self.Element.STYLE_SUPERSCRIPT, self.Element.STYLE_SUBSCRIPT):
                    if len(self.property) < 2:
                        return
                    parent_val = self.property[-2]
                    parent = self.Element(parent_val)
                    if parent.is_text:
                        self.text += self._apply_style(unescaped, elm_val)
                else:
                    self.text += unescaped

    @override
    def endElement(self, tag):
        """Signal the end of an element.

            Args:
                tag: The element tag.
            """
        if tag in (self.APP_DOC_ELEMENT, self.GRANT_DOC_ELEMENT):
            self._clean_data()
        self._end_registered_element(tag)

    @override
    def characters(self, content):
        """Receive notification of character data.

            Args:
                content: Data reported by the handler.
            """
        if self.property:
            elm_val = self.property[-1]
            element = self.Element(elm_val)
            if element.is_text:
                if element in (self.Element.STYLE_SUPERSCRIPT, self.Element.STYLE_SUBSCRIPT):
                    if len(self.property) < 2:
                        return
                    parent_val = self.property[-2]
                    parent = self.Element(parent_val)
                    if parent.is_text:
                        self.text += self._apply_style(content, elm_val)
                else:
                    self.text += content

    def _start_registered_elements(self, tag: str, attributes: AttributesImpl) -> None:
        if tag in [member.value for member in self.Element]:
            if tag == self.Element.CLAIM_TEXT.value and self.property and (self.property[-1] == tag) and self.text.strip():
                self.claim += ' ' + self.text.strip()
                self.text = ''
            elif tag == self.Element.HEADING.value:
                level_attr: str = attributes.get('level', '')
                new_level: int = int(level_attr) if level_attr.isnumeric() else 1
                max_level = min(self.parents.keys())
                self.level = new_level + 1 if new_level + 1 in self.parents else max_level
            self.property.append(tag)

    def _end_registered_element(self, tag: str) -> None:
        if tag in [item.value for item in self.Element] and self.property:
            current_tag = self.property.pop()
            self._add_property(current_tag, self.text.strip())

    def _add_property(self, name: str, text: str) -> None:
        if not name or not self.doc:
            return
        if name == self.Element.TITLE.value:
            if text:
                self.parents[self.level + 1] = self.doc.add_title(parent=self.parents[self.level], text=text)
                self.level += 1
            self.text = ''
        elif name == self.Element.ABSTRACT.value:
            if self.abstract:
                heading_text = PatentHeading.ABSTRACT.value
                heading_level = PatentHeading.ABSTRACT.level if PatentHeading.ABSTRACT.level in self.parents else 1
                abstract_item = self.doc.add_heading(heading_text, level=heading_level, parent=self.parents[heading_level])
                self.doc.add_text(label=DocItemLabel.PARAGRAPH, text=self.abstract, parent=abstract_item)
        elif name == self.Element.CLAIM_TEXT.value:
            text = re.sub('\\s+', ' ', text).strip()
            if text:
                self.claim += ' ' + text
            self.text = ''
        elif name == self.Element.CLAIM.value and self.claim:
            self.claims.append(self.claim.strip())
            self.claim = ''
        elif name == self.Element.CLAIMS.value and self.claims:
            heading_text = PatentHeading.CLAIMS.value
            heading_level = PatentHeading.CLAIMS.level if PatentHeading.CLAIMS.level in self.parents else 1
            claims_item = self.doc.add_heading(heading_text, level=heading_level, parent=self.parents[heading_level])
            for text in self.claims:
                self.doc.add_text(label=DocItemLabel.PARAGRAPH, text=text, parent=claims_item)
        elif name == self.Element.PARAGRAPH.value and text:
            text = re.sub('\\s+', ' ', text)
            if self.Element.ABSTRACT.value in self.property:
                self.abstract = self.abstract + ' ' + text if self.abstract else text
            else:
                self.doc.add_text(label=DocItemLabel.PARAGRAPH, text=text, parent=self.parents[self.level])
            self.text = ''
        elif name == self.Element.HEADING.value and text:
            self.parents[self.level + 1] = self.doc.add_heading(text=text, level=self.level, parent=self.parents[self.level])
            self.level += 1
            self.text = ''
        elif name == self.Element.TABLE.value:
            empty_table = TableData(num_rows=0, num_cols=0, table_cells=[])
            self.doc.add_table(data=empty_table, parent=self.parents[self.level])

    def _apply_style(self, text: str, style_tag: str) -> str:
        """Apply an HTML style to text.

            Args:
                text: A string containing plain text.
                style_tag: An HTML tag name for styling text. If the tag name is not
                  recognized as one of the supported styles, the method will return
                  the original `text`.

            Returns:
                A string after applying the style.
            """
        formatted = text
        if style_tag == self.Element.STYLE_SUPERSCRIPT.value:
            formatted = html.unescape(self.style_html.get_superscript(text))
        elif style_tag == self.Element.STYLE_SUBSCRIPT.value:
            formatted = html.unescape(self.style_html.get_subscript(text))
        return formatted

    def _clean_data(self) -> None:
        """Reset the variables from stream data."""
        self.property = []
        self.claim = ''
        self.claims = []
        self.abstract = ''
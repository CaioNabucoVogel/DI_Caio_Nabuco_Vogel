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
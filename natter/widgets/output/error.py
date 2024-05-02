"""Widget for displaying an error."""

##############################################################################
# Textual imports.
from textual.widgets import Label


##############################################################################
class Error(Label):
    """A widget to show an error."""

    DEFAULT_CSS = """
    Error {
        background: $error;
        width: 1fr;
        padding: 1 2;
        border: none;
        border-left: blank;
    }
    """


### error.py ends here

"""Widgets for showing the output."""

##############################################################################
# Textual imports.
from textual.widgets import Label, Markdown

##############################################################################
class Agent(Markdown):
    """A widget to show agent chat."""

    DEFAULT_CSS = """
    Agent {
        margin-left: 5;
        background: $boost;
    }
    """

##############################################################################
class User(Label):
    """A widget to show user chat."""

    DEFAULT_CSS = """
    User {
        width: 1fr;
        content-align-horizontal: right;
        margin-right: 5;
        background: $boost;
    }
    """

### output.py ends here

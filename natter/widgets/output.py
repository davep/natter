"""Widgets for showing the output."""

##############################################################################
# Textual imports.
from textual.widgets import Label, Markdown


##############################################################################
class Agent(Markdown):
    """A widget to show agent chat."""

    DEFAULT_CSS = """
    Agent {
        background: $primary-background;
        margin: 0;
        padding: 1 2;
        MarkdownFence {
            margin: 1 2;
            max-height: initial;
        }
    }
    """


##############################################################################
class User(Label):
    """A widget to show user chat."""

    DEFAULT_CSS = """
    User {
        background: $secondary-background;
        width: 1fr;
        padding: 1 2;
    }
    """


##############################################################################
class Error(User):
    """A widget to show an error."""

    DEFAULT_CSS = """
    Error {
        background: $error;
    }
    """


### output.py ends here

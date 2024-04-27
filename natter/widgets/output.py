"""Widgets for showing the output."""

##############################################################################
# Python imports.
from typing import Final

##############################################################################
# Textual imports.
from textual.await_complete import AwaitComplete
from textual.widgets import Label, Markdown


##############################################################################
class Agent(Markdown):
    """A widget to show agent chat."""

    ROLE: Final[str] = "assistant"
    """The role of this output."""

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

    def update(self, markdown: str) -> AwaitComplete:
        """Update the document with new Markdown.

        Args:
            markdown: A string containing Markdown.

        Returns:
            An optionally awaitable object. Await this to ensure that all
            children have been mounted.
        """
        # Update the internal copy of the markdown; this is normally only
        # used in the constructor to delay parsing of the document, but
        # doing it here too means that it can be used to access the raw text
        # later on.
        self._markdown = markdown
        return super().update(markdown)

    @property
    def raw_text(self) -> str:
        """The raw text."""
        return self._markdown


##############################################################################
class User(Label):
    """A widget to show user chat."""

    ROLE: Final[str] = "user"
    """The role of this output."""

    DEFAULT_CSS = """
    User {
        background: $secondary-background;
        width: 1fr;
        padding: 1 2;
    }
    """

    def __init__(self, output: str) -> None:
        super().__init__(output)
        self._raw_text = output

    @property
    def raw_text(self) -> str:
        """The raw text."""
        return self._raw_text


##############################################################################
class Error(Label):
    """A widget to show an error."""

    DEFAULT_CSS = """
    Error {
        background: $error;
        width: 1fr;
        padding: 1 2;
    }
    """


### output.py ends here

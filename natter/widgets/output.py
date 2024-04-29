"""Widgets for showing the output."""

##############################################################################
# Python imports.
from dataclasses import dataclass
from typing import Final

##############################################################################
# Textual imports.
from textual.await_complete import AwaitComplete
from textual.containers import VerticalScroll
from textual.message import Message
from textual.widgets import Label, Markdown


##############################################################################
class Output(VerticalScroll, can_focus=False):
    """Container for displaying the output."""

    DEFAULT_CSS = """
    Output {
        background: $primary-background;
    }
    """


##############################################################################
class Agent(Markdown, can_focus=True):
    """A widget to show agent chat."""

    ROLE: Final[str] = "assistant"
    """The role of this output."""

    DEFAULT_CSS = """
    Agent {
        background: $primary-background;
        margin: 0;
        padding: 1 2;
        border: none;
        border-left: blank;
        MarkdownFence {
            margin: 1 2;
            max-height: initial;
        }
        &:focus {
            border-left: thick $primary;
        }
    }
    """

    BINDINGS = [
        ("c", "copy"),
    ]

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

    def action_copy(self) -> None:
        """Copy the raw text of this widget to the clipboard."""
        self.app.copy_to_clipboard(self.raw_text)
        self.notify("Agent output copied to the clipboard", title="Copied")


##############################################################################
class User(Label, can_focus=True):
    """A widget to show user chat."""

    ROLE: Final[str] = "user"
    """The role of this output."""

    DEFAULT_CSS = """
    User {
        background: $secondary-background;
        width: 1fr;
        padding: 1 2;
        border: none;
        border-left: blank;
        &:focus {
            border-left: thick $primary;
        }
    }
    """

    BINDINGS = [
        ("enter", "edit"),
        ("c", "copy"),
    ]

    def __init__(self, output: str) -> None:
        super().__init__(output)
        self._raw_text = output

    @property
    def raw_text(self) -> str:
        """The raw text."""
        return self._raw_text

    @dataclass
    class Edit(Message):
        """Message sent when the user wants to edit their input."""

        text: str
        """The text the user wants to edit."""

    def action_edit(self) -> None:
        """Post a message providing text to edit."""
        self.post_message(self.Edit(self.raw_text))

    def action_copy(self) -> None:
        """Copy the raw text of this widget to the clipboard."""
        self.app.copy_to_clipboard(self.raw_text)
        self.notify("User input copied to the clipboard", title="Copied")


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


### output.py ends here

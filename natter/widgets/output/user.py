"""A widget for displaying the input from the user."""

##############################################################################
# Python imports.
from dataclasses import dataclass
from typing import Final

##############################################################################
# Textual imports.
from textual.message import Message
from textual.widgets import Label


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


### user.py ends here
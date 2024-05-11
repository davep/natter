"""A widget for displaying the input from the user."""

##############################################################################
# Python imports.
from dataclasses import dataclass

##############################################################################
# Ollama imports.
from ollama import Message

##############################################################################
# Textual imports.
from textual.message import Message as TextualMessage
from textual.widgets import Label


##############################################################################
class User(Label, can_focus=True):
    """A widget to show user chat."""

    DEFAULT_CSS = """
    User {
        background: $secondary-background;
        width: 1fr;
    }
    """

    BINDINGS = [
        ("enter", "edit"),
        ("c", "copy"),
    ]

    def __init__(self, output: Message | str) -> None:
        """Initialise the user's output.

        Args:
            output: The user's output.
        """
        self._raw_text = output if isinstance(output, str) else output["content"]
        super().__init__(self._raw_text)

    @property
    def raw_text(self) -> str:
        """The raw text."""
        return self._raw_text

    @dataclass
    class Edit(TextualMessage):
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

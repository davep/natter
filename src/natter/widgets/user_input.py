"""A widget for getting user input."""

##############################################################################
# Backward compatibility.
from __future__ import annotations

##############################################################################
# Python imports.
from dataclasses import dataclass

##############################################################################
# Textual imports.
from textual.events import Key
from textual.message import Message
from textual.widgets import TextArea


##############################################################################
class UserInput(TextArea):
    """The user input widget."""

    DEFAULT_CSS = """
    UserInput {
        background: $secondary-background;
        padding: 1;
        border: none;
        border-left: blank;
        height: auto;
        max-height: 25%;
        &> .text-area--cursor-line {
            background: initial;
        }
        &:focus {
            border: none;
            border-left: thick $primary;
        }
    }
    """

    BINDINGS = [
        ("insert, ctrl+v", "soft_enter"),
    ]

    @dataclass
    class Submitted(Message):
        """Message posted when the user submits input."""

        user_input: UserInput
        """The `UserInput` widget posting the message."""

        value: str
        """The value being submitted."""

        @property
        def control(self) -> UserInput:
            """Alias for self.user_input."""
            return self.user_input

    async def _on_key(self, event: Key) -> None:
        if event.key == "enter":
            self.post_message(self.Submitted(self, self.text))
            event.prevent_default()

    def action_soft_enter(self) -> None:
        """Action for create a new line."""
        self.insert("\n")


### user_input.py ends here

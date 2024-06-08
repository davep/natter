"""The widget that holds the conversation."""

##############################################################################
# Backward compatibility.
from __future__ import annotations

##############################################################################
# Python imports.
from types import TracebackType

##############################################################################
# Textual imports.
from textual.containers import VerticalScroll
from textual.widgets import LoadingIndicator

##############################################################################
# Typing extensions imports.
from typing_extensions import Self

##############################################################################
# Local imports.
from ...data import ConversationData
from .assistant import Assistant
from .error import Error
from .user import User


##############################################################################
class Interaction:
    """Context manager for an instance of interaction in the conversation."""

    def __init__(self, conversation: Conversation, user_input: str) -> None:
        """Initialise the interaction.

        Args:
            conversation: The conversation that this interaction is part of.
            user_input: The input from the user starting the interaction.
        """
        self._conversation = conversation
        self._user = User(user_input)
        self._assistant = Assistant()
        self._loading = LoadingIndicator()

    async def __aenter__(self) -> Self:
        """Mount the widgets needed for the interaction.

        Mounts the user's input, the space for the assistant's reply, and
        also the loading indicator.
        """
        await self._conversation.mount_all([self._user, self._assistant, self._loading])
        self._loading.anchor()
        return self

    async def update_response(self, response: str) -> None:
        """Update the interaction with the assistant's response.

        Args:
            response: The response to update with.
        """
        await self._assistant.update(self._assistant.raw_text + response)
        self._loading.anchor()

    async def abandon(self, reason: str) -> None:
        """Abandon the interaction.

        Args:
            reason: The reason to abandon the interaction.
        """
        await self._assistant.remove()
        await self._conversation.mount(error := Error(reason))
        error.anchor()

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_traceback: TracebackType | None,
    ) -> None:
        """Clean up at the end of the interaction.

        Removes the loading indicator.
        """
        del exc_type, exc_val, exc_traceback
        await self._loading.remove()


##############################################################################
class Conversation(VerticalScroll, can_focus=False):
    """Container for displaying a whole conversation."""

    DEFAULT_CSS = """
    Conversation {
        background: $primary-background;
        User, Assistant, Error {
            padding: 1;
            border: none;
            border-left: blank;
            &:focus {
                border-left: thick $primary;
            }
        }
    }
    """

    def __init__(self, initial_conversation: ConversationData | None = None) -> None:
        """Initialise the conversation.

        Args:
            initial_conversation: The initial conversation to show.
        """
        super().__init__(
            *[
                (User if ConversationData.is_user(part) else Assistant)(part)
                for part in initial_conversation or []
            ]
        )

    def interaction(self, user_input: str) -> Interaction:
        """Create an interaction within the conversation.

        Args:
            user_input: The input from the user.

        Returns:
            An `Interaction` context manager.
        """
        return Interaction(self, user_input)


### conversation.py ends here

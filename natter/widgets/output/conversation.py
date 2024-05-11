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
from .agent import Agent
from .error import Error
from .user import User


##############################################################################
class Conversation(VerticalScroll, can_focus=False):
    """Container for displaying a whole conversation."""

    DEFAULT_CSS = """
    Conversation {
        background: $primary-background;
    }
    """

    def __init__(self, initial_conversation: ConversationData | None = None) -> None:
        """Initialise the conversation.

        Args:
            initial_conversation: The initial conversation to show.
        """
        super().__init__(
            *[
                (User if ConversationData.is_user(part) else Agent)(part)
                for part in (
                    initial_conversation if initial_conversation is not None else []
                )
            ]
        )

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
            self._agent = Agent()
            self._loading = LoadingIndicator()

        async def __aenter__(self) -> Self:
            await self._conversation.mount_all([self._user, self._agent, self._loading])
            self._conversation.scroll_end()
            return self

        async def update_response(self, response: str) -> None:
            """Update the interaction with the agent's response.

            Args:
                response: The response to update with.
            """
            await self._agent.update(self._agent.raw_text + response)
            self._conversation.scroll_end()

        async def abandon(self, reason: str) -> None:
            """Abandon the interaction.

            Args:
                reason: The reason to abandon the interaction.
            """
            await self._agent.remove()
            await self._conversation.mount(Error(reason))

        async def __aexit__(
            self,
            exc_type: type[BaseException] | None,
            exc_val: BaseException | None,
            exc_traceback: TracebackType | None,
        ) -> None:
            del exc_type, exc_val, exc_traceback
            await self._loading.remove()

    def interaction(self, user_input: str) -> Interaction:
        """Create an interaction within the conversation.

        Args:
            user_input: The input from the user.

        Returns:
            An `Interaction` context manager.
        """
        return self.Interaction(self, user_input)

    @property
    def markdown(self) -> str:
        """The content of the conversation as a Markdown document."""
        document = ""
        for widget in self.children:
            if isinstance(widget, (User, Agent)):
                document += f"# {widget.__class__.__name__}\n\n{widget.raw_text}\n\n"
        return document


### conversation.py ends here

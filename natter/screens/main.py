"""The main screen."""

##############################################################################
# Python imports.
from asyncio import iscoroutine
from json import dumps, loads
from typing import Final

##############################################################################
# httpx imports.
from httpx import ConnectError

##############################################################################
# Ollama imports.
from ollama import AsyncClient, Message, ResponseError

##############################################################################
# Textual imports.
from textual import on, work
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.reactive import var
from textual.screen import Screen
from textual.widgets import LoadingIndicator

##############################################################################
# Local imports.
from ..data import conversations_dir
from ..widgets import Agent, Error, User, UserInput


##############################################################################
class Main(Screen[None]):
    """The main screen for the application."""

    CSS = """
    VerticalScroll {
        background: $primary-background;
    }

    VerticalScroll, UserInput {
        border: none;
        border-left: blank;
        &:focus {
            border-left: thick $primary;
        }
    }

    LoadingIndicator {
        width: 1fr;
        height: auto;
        content-align-horizontal: right;
        padding-right: 2;
    }
    """

    AUTO_FOCUS = "UserInput"

    _COMMAND_PREFIX: Final[str] = "/"
    """The prefix for commands."""

    _CONVERSATION_FILE: Final[str] = "conversation.json"
    """The name of the file to store the ongoing conversation in."""

    _client: var[AsyncClient] = var(AsyncClient)
    """The Ollama client."""

    _conversation: var[list[Message]] = var(list)
    """The ongoing conversation."""

    def __init__(self) -> None:
        """Initialise the main screen."""
        super().__init__()
        if (source := (conversations_dir() / self._CONVERSATION_FILE)).exists():
            self._conversation = loads(source.read_text())

    def compose(self) -> ComposeResult:
        yield VerticalScroll(
            *[
                {User.ROLE: User, Agent.ROLE: Agent}[part["role"]](part["content"])
                for part in self._conversation
            ]
        )
        yield UserInput()

    async def on_mount(self) -> None:
        """Settle the UI on startup."""
        self.query_one(VerticalScroll).scroll_end(animate=False)

    @on(UserInput.Submitted)
    async def handle_input(self, event: UserInput.Submitted) -> None:
        """Handle input from the user.

        Args:
            event: The input event to handle.
        """
        if event.value:
            self.query_one(UserInput).text = ""
            if event.value.startswith(self._COMMAND_PREFIX):
                await self.process_command(event.value[1:].lower())
            else:
                self.process_input(event.value)

    def _save_conversation(self) -> None:
        """Save the current conversation."""
        conversation: list[dict[str, str]] = []
        for widget in self.query_one(VerticalScroll).children:
            if isinstance(widget, (User, Agent)):
                conversation.append({"role": widget.ROLE, "content": widget.raw_text})
        (conversations_dir() / self._CONVERSATION_FILE).write_text(dumps(conversation))

    async def process_command(self, command: str) -> None:
        """Process a command."""
        if command == "new":
            self._conversation = []
            await self.query_one(VerticalScroll).remove_children()
            self.notify("Conversation cleared")
        else:
            self.notify(
                f"'[dim]{command}[/]' is an unknown command",
                title="Unknown command",
                severity="error",
            )

    @work
    async def process_input(self, text: str) -> None:
        """Process the input from the user.

        Args:
            text: The text to process.
        """
        await (output := self.query_one(VerticalScroll)).mount_all(
            [User(text), agent := Agent(), loading := LoadingIndicator()]
        )
        output.scroll_end()
        self._conversation.append({"role": "user", "content": text})
        chat = self._client.chat(
            model="llama3",
            messages=self._conversation,
            stream=True,
        )
        assert iscoroutine(chat)
        reply = ""
        try:
            async for part in await chat:
                reply += part["message"]["content"]
                await agent.update(reply)
                output.scroll_end()
                if part["message"]["content"]:
                    self._conversation.append(part["message"])
            self._save_conversation()
        except (ResponseError, ConnectError) as error:
            await agent.remove()
            self.notify(str(error), title="Ollama error", severity="error")
            await output.mount(Error(str(error)))
            output.scroll_end()
        finally:
            await loading.remove()


### main.py ends here

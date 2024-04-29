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
from textual.reactive import var
from textual.screen import Screen
from textual.widgets import LoadingIndicator

##############################################################################
# Textual-fspicker imports.
from textual_fspicker import FileSave, Filters

##############################################################################
# Local imports.
from ..data import conversations_dir
from ..widgets import Agent, Error, Output, User, UserInput


##############################################################################
class Main(Screen[None]):
    """The main screen for the application."""

    CSS = """
    LoadingIndicator {
        width: 1fr;
        height: auto;
        content-align-horizontal: right;
        padding-right: 2;
    }
    """

    AUTO_FOCUS = "UserInput"

    BINDINGS = [
        ("escape", "jump_to_input"),
    ]

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
        yield Output(
            *[
                {User.ROLE: User, Agent.ROLE: Agent}[part["role"]](part["content"])
                for part in self._conversation
            ]
        )
        yield UserInput()

    async def on_mount(self) -> None:
        """Settle the UI on startup."""
        self.query_one(Output).scroll_end(animate=False)

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
        for widget in self.query_one(Output).children:
            if isinstance(widget, (User, Agent)):
                conversation.append({"role": widget.ROLE, "content": widget.raw_text})
        (conversations_dir() / self._CONVERSATION_FILE).write_text(dumps(conversation))

    async def process_command(self, command: str) -> None:
        """Process a command."""
        if command == "new":
            self._conversation = []
            await self.query_one(Output).remove_children()
            self.notify("Conversation cleared")
        elif command == "save":
            self._save_conversation_text()
        elif command == "quit":
            self.app.exit()
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
        await (output := self.query_one(Output)).mount_all(
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

    @on(User.Edit)
    def edit_input(self, event: User.Edit) -> None:
        self.query_one(Output).scroll_end(animate=False)
        user_input = self.query_one(UserInput)
        user_input.text = event.text
        user_input.focus()

    @work
    async def _save_conversation_text(self) -> None:
        """Save the conversation as a Markdown document."""
        if (
            target := await self.app.push_screen_wait(
                FileSave(
                    ".",
                    filters=Filters(
                        (
                            "Markdown",
                            lambda p: p.suffix.lower() in (".md", ".markdown"),
                        ),
                        ("Text", lambda p: p.suffix.lower() in (".txt", ".text")),
                        ("Any", lambda _: True),
                    ),
                )
            )
        ) is None:
            return

        if not target.suffix:
            target = target.with_suffix(".md")

        document = ""
        for widget in self.query_one(Output).children:
            if isinstance(widget, (User, Agent)):
                document += f"# {widget.__class__.__name__}\n\n{widget.raw_text}\n\n"

        target.write_text(document)

        self.notify(str(target), title="Saved")

    def action_jump_to_input(self) -> None:
        """Jump to the input and scroll the output to the end."""
        if self.focused != (user_input := self.query_one(UserInput)):
            user_input.focus()
            self.query_one(Output).scroll_end(animate=False)
        elif self.focused == user_input:
            self.app.exit()


### main.py ends here

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

##############################################################################
# Local imports.
from ..data import conversations_dir
from ..widgets import Agent, Conversation, User, UserInput
from .save_conversation import SaveConversation


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
        ("escape", "escape"),
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
        if (source := conversations_dir() / self._CONVERSATION_FILE).exists():
            self._conversation = loads(source.read_text())

    def compose(self) -> ComposeResult:
        yield Conversation(
            *[
                {User.ROLE: User, Agent.ROLE: Agent}[part["role"]](part["content"])
                for part in self._conversation
            ]
        )
        yield UserInput()

    async def on_mount(self) -> None:
        """Settle the UI on startup."""
        self.query_one(Conversation).scroll_end(animate=False)

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
        for widget in self.query_one(Conversation).children:
            if isinstance(widget, (User, Agent)):
                conversation.append({"role": widget.ROLE, "content": widget.raw_text})
        (conversations_dir() / self._CONVERSATION_FILE).write_text(dumps(conversation))

    async def process_command(self, command: str) -> None:
        """Process a command."""
        match command:
            case "new":
                self._conversation = []
                await self.query_one(Conversation).remove_children()
                self.notify("Conversation cleared")
            case "save":
                self._save_conversation_text()
            case "quit":
                self.app.exit()
            case _:
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
        self._conversation.append({"role": "user", "content": text})
        chat = self._client.chat(
            model="llama3",
            messages=self._conversation,
            stream=True,
        )
        assert iscoroutine(chat)
        async with self.query_one(Conversation).interaction(text) as interaction:
            try:
                async for part in await chat:
                    if part["message"]["content"]:
                        await interaction.update_response(part["message"]["content"])
                        self._conversation.append(part["message"])
            except (ResponseError, ConnectError) as error:
                await interaction.abandon(str(error))
            else:
                self._save_conversation()

    @on(User.Edit)
    def edit_input(self, event: User.Edit) -> None:
        """Make user input available for editing.

        Args:
            event: The event to handle.
        """
        self.query_one(Conversation).scroll_end(animate=False)
        user_input = self.query_one(UserInput)
        user_input.text = event.text
        user_input.focus()

    @work
    async def _save_conversation_text(self) -> None:
        """Save the conversation as a Markdown document."""
        # Prompt the user with a save dialog, to get the name of a file to
        # save to.
        if (target := await SaveConversation.get_filename(self)) is None:
            return

        # Gather up the content of the conversation as a Markdown document.
        document = ""
        for widget in self.query_one(Conversation).children:
            if isinstance(widget, (User, Agent)):
                document += f"# {widget.__class__.__name__}\n\n{widget.raw_text}\n\n"

        # Save the Markdown to the target file, adding a 'md' extension if
        # no extension was specified.
        (target if target.suffix else target.with_suffix(".md")).write_text(document)

        # Let the user know the save happened.
        self.notify(str(target), title="Saved")

    def action_escape(self) -> None:
        """Process the escape request based on current context."""
        if self.focused != (user_input := self.query_one(UserInput)):
            user_input.focus()
            self.query_one(Conversation).scroll_end(animate=False)
        elif self.focused == user_input:
            self.app.exit()


### main.py ends here

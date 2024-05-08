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
from ollama import AsyncClient, ResponseError

##############################################################################
# Textual imports.
from textual import on, work
from textual.app import ComposeResult
from textual.reactive import var
from textual.screen import Screen

##############################################################################
# Local imports.
from ..data import ConversationData, conversations_dir
from ..widgets import Conversation, User, UserInput
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

    _conversation: var[ConversationData] = var(ConversationData("Untitled", "llama3"))
    """The ongoing conversation."""

    def __init__(self) -> None:
        """Initialise the main screen."""
        super().__init__()
        if (source := conversations_dir() / self._CONVERSATION_FILE).exists():
            self._conversation = ConversationData.from_json(loads(source.read_text()))

    def compose(self) -> ComposeResult:
        yield Conversation(self._conversation)
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
                await self.process_command(event.value[1:].lower().strip())
            else:
                self.process_input(event.value)

    def _save_conversation(self) -> None:
        """Save the current conversation."""
        (conversations_dir() / self._CONVERSATION_FILE).write_text(
            dumps(self._conversation.json)
        )

    async def process_command(self, command: str) -> None:
        """Process a command."""
        match command:
            case "new":
                self._conversation = ConversationData("Untitled", "llama3")
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
        self._conversation.record({"role": "user", "content": text})
        chat = self._client.chat(
            model=self._conversation.model,
            messages=self._conversation.history,
            stream=True,
        )
        assert iscoroutine(chat)
        async with self.query_one(Conversation).interaction(text) as interaction:
            try:
                async for part in await chat:
                    if part["message"]["content"]:
                        await interaction.update_response(part["message"]["content"])
                        self._conversation.record(part["message"])
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

        # If the user didn't give an extension, add a default.
        if not target.suffix:
            target = target.with_suffix(".md")

        # Save the Markdown to the target file.
        target.write_text(self.query_one(Conversation).markdown)

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

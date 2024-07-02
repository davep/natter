"""The main screen."""

##############################################################################
# Python imports.
from json import dumps, loads
from typing import Any, Coroutine, Final

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

    _client: var[AsyncClient | None] = var(None)
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
            dumps(self._conversation.json, indent=4)
        )

    async def process_command(self, command: str) -> None:
        """Process a command."""
        match command.split():
            case ["new"]:
                self.stop_interaction()
                self._conversation = ConversationData("Untitled", "llama3")
                self._save_conversation()
                await self.query_one(Conversation).remove_children()
                self.notify("Conversation cleared")
            case ["save"]:
                self._save_conversation_text()
            case ["host"]:
                if self._conversation.host:
                    self.notify(f"Currently connected to {self._conversation.host}")
                else:
                    self.notify("Currently connected to the default host")
            case ["host", host]:
                self._conversation.host = host
                self._client = None
                self.notify(f"Host set to {host}")
            case ["quit"]:
                self.app.exit()
            case _:
                self.notify(
                    f"'[dim]{command}[/]' is an unknown command",
                    title="Unknown command",
                    severity="error",
                )

    _INTERACTION_GROUP: Final[str] = "--natter-interaction"
    """The name of the worker group for doing interaction with Ollama."""

    @work(exclusive=True, group=_INTERACTION_GROUP)
    async def process_input(self, text: str) -> None:
        """Process the input from the user.

        Args:
            text: The text to process.
        """
        if self._client is None:
            self._client = AsyncClient(self._conversation.host)
        self._conversation.record({"role": "user", "content": text})
        chat: Coroutine[Any, Any, Any] = self._client.chat(
            model=self._conversation.model,
            messages=list(self._conversation),
            stream=True,
        )
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

    def stop_interaction(self) -> None:
        """Stop any ongoing interaction."""
        self.workers.cancel_group(self, self._INTERACTION_GROUP)

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
        target.write_text(self._conversation.markdown)

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

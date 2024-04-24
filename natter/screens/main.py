"""The main screen."""

##############################################################################
# Textual imports.
from asyncio import iscoroutine
from textual import on, work
from textual.app import ComposeResult
from textual.reactive import var
from textual.screen import Screen
from textual.widgets import Markdown

##############################################################################
# Ollama imports.
from ollama import AsyncClient, Message

##############################################################################
# Local imports.
from ..widgets import UserInput

##############################################################################
class Main(Screen):
    """The main screen for the application."""

    CSS = """
    Main {
        &> Markdown {
            height: 1fr;
        }
    }
    """

    conversation: var[list[Message]] = var(list)
    """The ongoing conversation."""

    def compose(self) -> ComposeResult:
        yield Markdown()
        yield UserInput()

    @on(UserInput.Submitted)
    def handle_input(self, event: UserInput.Submitted) -> None:
        """Handle input from the user.

        Args:
            event: The input event to handle.
        """
        self.query_one(UserInput).text = ""
        self.process_input(event.value)

    @work
    async def process_input(self, text: str) -> None:
        chat = AsyncClient().chat(
            model="llama3",
            messages=[
                *self.conversation,
                {"role": "user", "content": text}
            ],
            stream=True,
        )
        assert iscoroutine(chat)
        reply = ""
        async for part in await chat:
            reply += part["message"]["content"]
            self.query_one(Markdown).update(reply)
            if part["message"]["content"]:
                self.conversation.append(part["message"])

### main.py ends here

"""The main screen."""

##############################################################################
# Python imports.
from asyncio import iscoroutine

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

##############################################################################
# Local imports.
from ..widgets import Agent, Error, User, UserInput


##############################################################################
class Main(Screen):
    """The main screen for the application."""

    AUTO_FOCUS = "UserInput"

    conversation: var[list[Message]] = var(list)
    """The ongoing conversation."""

    def compose(self) -> ComposeResult:
        yield VerticalScroll()
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
        """Process the input from the user.

        Args:
            text: The text to process.
        """
        await self.query_one(VerticalScroll).mount(output := User(text))
        self.scroll_to_widget(output)
        chat = AsyncClient().chat(
            model="llama3",
            messages=[*self.conversation, {"role": "user", "content": text}],
            stream=True,
        )
        assert iscoroutine(chat)
        reply = ""
        await self.query_one(VerticalScroll).mount(output := Agent())
        try:
            async for part in await chat:
                reply += part["message"]["content"]
                await output.update(reply)
                self.scroll_to_widget(output)
                if part["message"]["content"]:
                    self.conversation.append(part["message"])
        except (ResponseError, ConnectError) as error:
            await output.remove()
            self.notify(str(error), title="Ollama error", severity="error")
            await self.query_one(VerticalScroll).mount(output := Error(str(error)))
            self.scroll_to_widget(output)


### main.py ends here

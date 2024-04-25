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
from textual.widgets import LoadingIndicator

##############################################################################
# Local imports.
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

    _client: var[AsyncClient] = var(AsyncClient)
    """The Ollama client."""

    _conversation: var[list[Message]] = var(list)
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
        await self.query_one(VerticalScroll).mount(User(text))
        self.query_one(VerticalScroll).scroll_end()
        chat = self._client.chat(
            model="llama3",
            messages=[*self._conversation, {"role": "user", "content": text}],
            stream=True,
        )
        assert iscoroutine(chat)
        reply = ""
        await self.query_one(VerticalScroll).mount(output := Agent())
        await self.query_one(VerticalScroll).mount(loading := LoadingIndicator())
        try:
            async for part in await chat:
                reply += part["message"]["content"]
                await output.update(reply)
                self.query_one(VerticalScroll).scroll_end()
                if part["message"]["content"]:
                    self._conversation.append(part["message"])
        except (ResponseError, ConnectError) as error:
            await output.remove()
            self.notify(str(error), title="Ollama error", severity="error")
            await self.query_one(VerticalScroll).mount(Error(str(error)))
            self.query_one(VerticalScroll).scroll_end()
        finally:
            await loading.remove()


### main.py ends here

"""Widget that shows the output from the agent."""

##############################################################################
# Ollama imports.
from ollama import Message

##############################################################################
# Textual imports.
from textual.await_complete import AwaitComplete
from textual.widgets import Markdown


##############################################################################
class Agent(Markdown, can_focus=True):
    """A widget to show agent chat."""

    DEFAULT_CSS = """
    Agent {
        background: $primary-background;
        margin: 0;
        padding: 1 2;
        border: none;
        border-left: blank;
        MarkdownFence {
            margin: 1 2;
            max-height: initial;
        }
        &:focus {
            border-left: thick $primary;
        }
    }
    """

    BINDINGS = [
        ("c", "copy"),
    ]

    def __init__(self, output: Message | str = ""):
        """Initialise the agent output.

        Args:
            output: Any initial output.
        """
        super().__init__(output if isinstance(output, str) else output["content"])

    def update(self, markdown: str) -> AwaitComplete:
        """Update the document with new Markdown.

        Args:
            markdown: A string containing Markdown.

        Returns:
            An optionally awaitable object. Await this to ensure that all
            children have been mounted.
        """
        # Update the internal copy of the markdown; this is normally only
        # used in the constructor to delay parsing of the document, but
        # doing it here too means that it can be used to access the raw text
        # later on.
        self._markdown = markdown
        return super().update(markdown)

    @property
    def raw_text(self) -> str:
        """The raw text."""
        return self._markdown or ""

    def action_copy(self) -> None:
        """Copy the raw text of this widget to the clipboard."""
        self.app.copy_to_clipboard(self.raw_text)
        self.notify("Agent output copied to the clipboard", title="Copied")


### agent.py ends here

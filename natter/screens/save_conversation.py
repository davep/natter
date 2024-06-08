"""Provides a modal dialog for prompting for a save screen."""

##############################################################################
# Python imports.
from pathlib import Path

##############################################################################
# Textual imports.
from textual.screen import Screen

##############################################################################
# Textual-fspicker imports.
from textual_fspicker import FileSave, Filters


##############################################################################
class SaveConversation(FileSave):
    """Modal dialog for prompting for the name of a conversation file."""

    def __init__(self) -> None:
        super().__init__(
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

    @classmethod
    async def get_filename(cls, screen: Screen[None]) -> Path | None:
        """Get the filename from the user.

        Args:
            screen: The parent screen.

        Returns:

            The path of the file the user selected, or `None` if they
            cancelled.
        """
        return await screen.app.push_screen_wait(cls())


### save_conversation.py ends here

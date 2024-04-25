"""The main application class."""

##############################################################################
# Textual imports.
from textual.app import App

##############################################################################
# Local imports.
from .screens import Main


##############################################################################
class Natter(App[None]):
    """The Natter application."""

    ENABLE_COMMAND_PALETTE = False

    def on_mount(self) -> None:
        """Show the main screen once the app is mounted."""
        self.push_screen(Main())


### app.py ends here

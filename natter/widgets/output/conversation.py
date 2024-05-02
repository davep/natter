"""The widget that holds the conversation."""

##############################################################################
# Textual imports.
from textual.containers import VerticalScroll


##############################################################################
class Conversation(VerticalScroll, can_focus=False):
    """Container for displaying a whole conversation."""

    DEFAULT_CSS = """
    Conversation {
        background: $primary-background;
    }
    """


### conversation.py ends here

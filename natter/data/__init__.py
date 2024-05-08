"""Data-related code for the application."""

##############################################################################
# Local imports.
from .conversation_data import ConversationData
from .locations import conversations_dir, data_dir

##############################################################################
# Exports.
__all__ = ["ConversationData", "conversations_dir", "data_dir"]

### __init__.py ends here

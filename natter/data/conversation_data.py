"""Class that holds details of a conversation."""

##############################################################################
# Backward compatibility.
from __future__ import annotations

##############################################################################
# Python imports.
from dataclasses import dataclass, field
from typing import Any, Iterator

##############################################################################
# Ollama imports.
from ollama import Message

##############################################################################
# Typing extensions imports.
from typing_extensions import Self


##############################################################################
@dataclass
class ConversationData:
    """Details and history of a conversation."""

    title: str
    """The title of the conversation."""

    model: str
    """The name of the model in use with this conversation."""

    history: list[Message] = field(default_factory=list)
    """The history of the conversation."""

    host: str = ""
    """The host the conversation is being held with."""

    @staticmethod
    def is_user(message: Message) -> bool:
        """Is the given message from the user?

        Args:
            message: The message to check.

        Returns:
            `True` if it's from the user, `False` if not.
        """
        return message["role"] == "user"

    @staticmethod
    def is_assistant(message: Message) -> bool:
        """Is the given message from the assistant?

        Args:
            message: The message to check.

        Returns:
            `True` if it's from the assistant, `False` if not.
        """
        return message["role"] == "assistant"

    def record(self, message: Message) -> Self:
        """Record the given message in the history.

        Args:
            message: The message to record.

        Returns:
            Self.
        """
        # If the role of the given message is the same as the previous role...
        if self.history and message["role"] == self.history[-1]["role"]:
            # ...accumulate the content into the last message in the
            # history.
            self.history[-1]["content"] += message["content"]
        else:
            # Otherwise start a new message.
            self.history.append(message)
        return self

    @property
    def json(self) -> dict[str, Any]:
        """The conversation data as a JSON-friendly structure."""
        return {
            "title": self.title,
            "model": self.model,
            "history": self.history,
            "host": self.host,
        }

    @property
    def markdown(self) -> str:
        """The content of the conversation as a Markdown document."""
        return "\n\n".join(
            f"# {'User' if self.is_user(part) else 'Assistant'}\n\n{part['content']}"
            for part in self
        )

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> ConversationData:
        """Create an instance of the class from JSON data.

        Args:
            data: The data to create it from.

        Returns:
            A fresh instance of the class with all data loaded.
        """
        return cls(
            data.get("title", "Untitled"),
            data.get("model", "llama3"),
            data.get("history", []),
            data.get("host", ""),
        )

    def __iter__(self) -> Iterator[Message]:
        return iter(self.history)


### conversation_data.py ends here

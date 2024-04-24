"""Main entry point for the application."""

##############################################################################
# Local imports.
from .app import Natter


##############################################################################
def run() -> None:
    """Run the application."""
    Natter().run()


##############################################################################
if __name__ == "__main__":
    run()


### __main__.py ends here

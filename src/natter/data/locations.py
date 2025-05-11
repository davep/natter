"""Functions for getting data locations."""

##############################################################################
# Python imports.
from pathlib import Path

##############################################################################
# XDG imports.
from xdg_base_dirs import xdg_data_home


##############################################################################
def data_dir() -> Path:
    """The path to the data directory for the application.

    Returns:
        The path to the data directory for the application.

    Note:
        If the directory doesn't exist, it will be created as a side-effect
        of calling this function.
    """
    (save_to := xdg_data_home() / "natter").mkdir(parents=True, exist_ok=True)
    return save_to


##############################################################################
def conversations_dir() -> Path:
    """The path to the conversations directory.

    Returns:
        The path to the conversations directory.

    Note:
        If the directory doesn't exist, it will be created as a side-effect
        of calling this function.
    """
    (save_to := data_dir() / "conversations").mkdir(parents=True, exist_ok=True)
    return save_to


### locations.py ends here

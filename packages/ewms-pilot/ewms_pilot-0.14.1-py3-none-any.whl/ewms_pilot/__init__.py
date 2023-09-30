"""Init."""


from .pilot import consume_and_reply
from .tasks.io import FileType

__all__ = [
    "consume_and_reply",
    "FileType",
]

# version is a human-readable version number.
__version__ = "0.14.1"

# version_info is a four-tuple for programmatic comparison. The first
# three numbers are the components of the version number. The fourth
# is zero for an official release, positive for a development branch,
# or negative for a release candidate or beta (after the base version
# number has been incremented)
version_info = (
    int(__version__.split(".")[0]),
    int(__version__.split(".")[1]),
    int(__version__.split(".")[2]),
    0,
)

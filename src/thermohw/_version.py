"""The version of thermohw."""
from typing import Tuple

__version_info__: Tuple[int, int, int, str] = (0, 7, 2, "dev0")
__version__ = ".".join(str(v) for v in __version_info__ if str(v))

"""The version of thermohw."""
from typing import Tuple

__version_info__: Tuple[int, int, int] = (0, 1, 0)
__version__: str = '.'.join(map(str, __version_info__[:3]))
if len(__version_info__) == 4:
    __version__ += __version_info__[-1]

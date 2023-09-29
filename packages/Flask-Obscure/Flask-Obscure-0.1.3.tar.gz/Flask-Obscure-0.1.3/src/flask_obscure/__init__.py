from pkg_resources import get_distribution, DistributionNotFound
from .obscure import Obscure, converters, Num, Hex, Base32, Base64, Tame

__all__ = [
    "__version__",
    "Obscure",
    "converters",
    "Num",
    "Hex",
    "Base32",
    "Base64",
    "Tame",
]

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    pass  # package is not installed

import big
from .version import Version

version = Version(big.__version__)

del Version
del big

""" This module replaces the Pythonista3 builtin modules for calling shortcuts. This will work either in PyTo or Mac
>>> from minimock import Mock
>>> fn = Mock('print')
>>> fn('Test')
Called print('Test')

"""

from .version import version
from .util import tomlrc

__all__ = ["version", "tomlrc"]

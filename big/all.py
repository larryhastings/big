#!/usr/bin/env python3

"""
The big package is a grab-bag of cool code for use in your programs.

Think big!
"""

_license = """
big
Copyright 2022-2024 Larry Hastings
All rights reserved.

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR
THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""


import big

__all__ = ['_license']

from . import boundinnerclass
__all__.extend(boundinnerclass.__all__)
from .boundinnerclass import *

from . import builtin
__all__.extend(builtin.__all__)
from .builtin import *

from . import deprecated
# we DON'T splat all the symbols from deprecated into big.all!

from . import file
__all__.extend(file.__all__)
from .file import *

from . import graph
__all__.extend(graph.__all__)
from .graph import *

from . import heap
__all__.extend(heap.__all__)
from .heap import *

from . import itertools
__all__.extend(itertools.__all__)
from .itertools import *

from . import log
__all__.extend(log.__all__)
from .log import *

from . import metadata
# we DON'T splat all symbols from metadata into big.all, either.

from . import scheduler
__all__.extend(scheduler.__all__)
from .scheduler import *

from . import state
__all__.extend(state.__all__)
from .state import *

from . import text
__all__.extend(text.__all__)
from .text import *

from . import time
__all__.extend(time.__all__)
from .time import *

from . import version
__all__.extend(version.__all__)
from .version import *

__version__ = big.__version__
__all__.append('__version__')


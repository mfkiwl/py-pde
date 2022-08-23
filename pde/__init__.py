"""
The py-pde package provides classes and methods for solving partial differential
equations.
"""

# initialize the configuration
from .tools.config import Config, environment

config = Config()  # initialize the default configuration
del Config  # clean the name space

# import all other modules that should occupy the main name space
from .fields import *  # @UnusedWildImport
from .grids import *  # @UnusedWildImport
from .pdes import *  # @UnusedWildImport
from .solvers import *  # @UnusedWildImport
from .storage import *  # @UnusedWildImport
from .tools.config import check_package_version  # temporary import, deleted below
from .tools.parameters import Parameter
from .trackers import *  # @UnusedWildImport
from .version import __version__
from .visualization import *  # @UnusedWildImport

# The code below is generated by scripts/create_requirements.txt
# GENERATED CODE – anything you modify below might be overwritten automatically
check_package_version("matplotlib", "3.1.0")
check_package_version("numba", "0.50.0")
check_package_version("numpy", "1.22.0")
check_package_version("scipy", "1.4.0")
check_package_version("sympy", "1.5.0")
del check_package_version

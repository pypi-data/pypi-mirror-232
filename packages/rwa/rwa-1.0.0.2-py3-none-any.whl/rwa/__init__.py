"""rwa module. Imports all classes from the shared object file (.so) 
into the `rwa`-namespace. Use e.g. as:
`from rwa import JointType`
"""
from .rwaPython.rwa import *  # pylint: disable=import-error # noqa: F403

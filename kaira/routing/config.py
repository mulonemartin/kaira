
""" ``config`` module.
"""

from .choice import try_build_choice_route
from .curly import default_pattern as curly_default_pattern
from .curly import patterns as curly_patterns
from .curly import try_build_curly_route
from .plain import try_build_plain_route
from .regex import try_build_regex_route


assert curly_default_pattern
assert curly_patterns

route_builders = [
    try_build_plain_route,
    try_build_choice_route,
    try_build_curly_route,
    try_build_regex_route
]

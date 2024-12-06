from typing import Set
from pb_instance import PB

# Absract class for rules
class Rule:
    # Returns a feasible subset of projects
    def apply(self, pb: PB)->Set[Set[str]]:
        None

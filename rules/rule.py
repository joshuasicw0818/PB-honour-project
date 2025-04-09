from typing import Set
from pb_instance import PB

# Absract class for rules
class Rule:
    # Returns a feasible subset of projects
    def apply(self, pb: PB, rsg: bool, rank: int, share:float)->Set[Set[str]]:
        """
        Apply the rule to the given PB instance and return a feasible subset of projects.
        Parameters:
        - pb: The PB instance containing the projects, voters, etc.
        - rsg: A boolean indicating whether to use the RSG method.
        - rank: The rank of the projects for RSG
        - share: The share of the projects fo r RSG
        """
        None

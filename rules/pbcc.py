import numpy as np
from pb_instance import PB  # Import the PB instance class
from rules.rule import Rule  # Import the base Rule class

class PBCC(Rule):
    """
    The PBCC (Participatory Budgeting with a Consensus Criterion) rule class.

    This class implements a rule to select the subset of projects (from a set of feasible subsets)
    that maximizes a utility function based on the consensus criterion.
    """
    
    def apply(self, pb, rsg=False,rank=None, share=None):
        """
        Applies the PBCC rule to a given participatory budgeting instance.

        Parameters:
        - pb: A PB instance containing voters, projects, preferences, and other data.

        Returns:
        - A list of subsets (best_s) that maximize the consensus utility.
        """
        best_s = []  # List to store the best subsets
        best_u = -float('inf')  # Initialize the best utility as negative infinity

        # feasible subsets
        f = pb.f
        # If rank and share are provided, apply the RSG rule to get the feasible subsets
        if rsg:
            f = pb.rsg_f(rank, share)

        # Iterate through all feasible subsets of projects
        for s in f:
            util = 0  # Initialize utility for the current subset

            # Calculate utility for each voter
            for i in pb.N:
                # Find the minimum rank of any project in the subset for the current voter
                r = min([pb.rank(i, p) for p in s if pb.rank(i, p)], default=float('inf'))

                # Add the utility contribution from this voter
                util += pb.m - r

            # Update the best subset(s) if a higher utility is found
            if util > best_u:
                best_u = util  # Update the best utility
                best_s = [s]  # Replace the best subset list with the current subset
            elif util == best_u:
                best_s.append(s)  # Add to the list of subsets with the same utility

        return best_s  # Return the subset(s) with the highest utility
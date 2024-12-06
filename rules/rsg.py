from rules.rule import Rule

class RSG(Rule):
    """
    The RSG (Rank-Share Guarantee) rule class.

    This class implements a rule to select the subset of projects (from a set of feasible subsets)
    that maximizes the number of voters whose rank-share guarantee is satisfied.
    """
    def __init__(self, k, share):
        """
        Initializes the RSG rule with the given parameters.
        
        Parameters:
        - k: The maximum rank threshold.
        - share: The minimum budget share required to satisfy a voter.
        """
        self.k = k  # Rank threshold
        self.share = share  # Minimum budget share

    def apply(self, pb):
        """
        Applies the RSG rule to a given participatory budgeting instance.

        Parameters:
        - pb: A PB instance containing voters, projects, preferences, and other data.

        Returns:
        - A list of subsets (best_s) that maximize the number of satisfied voters.
        """
        best_s = []  # List to store the best subsets
        best_size = -float('inf')  # Initialize the best size as negative infinity

        # Iterate through all feasible subsets of projects
        for s in pb.f:
            # Count the number of voters satisfied by the current subset
            cnt = len([i for i in pb.N if self.t(i, s, pb) <= self.k])

            # Update the best subset(s) if a higher count is found
            if cnt > best_size:
                best_size = cnt  # Update the best count
                best_s = [s]  # Replace the best subset list with the current subset
            elif cnt == best_size:
                best_s.append(s)  # Add to the list of subsets with the same count

        return best_s  # Return the subset(s) that maximize the number of satisfied voters

    def t(self, voter, s, pb):
        """
        Calculates the smallest rank threshold such that the voter receives their share of the budget.

        Parameters:
        - voter: The voter being evaluated.
        - s: The current subset of projects.
        - pb: The PB instance.

        Returns:
        - The rank threshold j where the voter’s share is satisfied, or pb.m + 1 if not satisfied.
        """
        # If the total cost of the subset is less than the share, return a large rank
        if pb.cS(s) < self.share:
            return pb.m + 1

        # Iterate over possible ranks to find the smallest rank j that satisfies the share
        for j in range(1, pb.m + 1):
            # Find the projects in the subset with rank <= j for this voter
            inter = (p for p in s if pb.rank(voter, p) and pb.rank(voter, p) <= j)

            # Check if the total cost of these projects meets or exceeds the share
            if pb.cS(inter) >= self.share:
                return j

        # If no rank satisfies the share, return pb.m + 1
        return pb.m + 1